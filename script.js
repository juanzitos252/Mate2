// Estado da aplicação
const state = {
    currentQuestion: null,
    currentRoute: '',
    theme: 'light-theme',
    timedQuiz: {
        score: 0,
        timeLeft: 60,
        timer: null,
        isActive: false
    },
    memorization: {
        tableNumber: 0,
        questions: [],
        currentQuestionIndex: 0,
        correctAnswers: 0
    }
};

// Elementos da DOM
const app = document.getElementById('app');
const themeToggle = document.getElementById('theme-toggle');
const body = document.body;

// Funções de template para renderizar as telas
const templates = {
    home: () => `
        <div class="container text-center">
            <h1>Quiz Mestre da Tabuada</h1>
            <p>Aprenda e memorize a tabuada de forma divertida e adaptativa!</p>
            <div class="d-grid gap-2 col-6 mx-auto">
                <button class="btn btn-primary" data-route="quiz">Iniciar Quiz</button>
                <button class="btn btn-primary" data-route="quiz_invertido">Quiz Invertido</button>
                <button class="btn btn-primary" data-route="treino">Modo Treino</button>
                <button class="btn btn-primary" data-route="memorizacao">Modo Memorização</button>
                <button class="btn btn-primary" data-route="quiz_cronometrado">Modo Cronometrado</button>
                <hr>
                <button class="btn btn-secondary" data-route="formula_quiz_setup">Quiz com Fórmulas</button>
                <button class="btn btn-info" data-route="estatisticas">Estatísticas</button>
            </div>
        </div>
    `,
    quiz: () => `
        <div class="container text-center">
            <h1 id="question"></h1>
            <div id="options" class="row"></div>
            <p id="feedback"></p>
            <button class="btn btn-secondary" id="next-question" style="display: none;">Próxima Pergunta</button>
            <button class="btn btn-secondary" data-route="home">Voltar ao Menu</button>
        </div>
    `,
    quiz_invertido: () => `
        <div class="container text-center">
            <h1 id="question-inv"></h1>
            <div id="options-inv" class="row"></div>
            <p id="feedback-inv"></p>
            <button class="btn btn-secondary" id="next-question-inv" style="display: none;">Próxima Pergunta</button>
            <button class="btn btn-secondary" data-route="home">Voltar ao Menu</button>
        </div>
    `,
    treino: () => `
        <div class="container text-center">
            <h1>Modo Treino</h1>
            <h2 id="training-title"></h2>
            <div id="training-table"></div>
            <button class="btn btn-primary" id="check-answers">Verificar Respostas</button>
            <p id="training-summary"></p>
            <button class="btn btn-secondary" data-route="home">Voltar ao Menu</button>
        </div>
    `,
    estatisticas: () => `
        <div class="container">
            <h1 class="text-center">Estatísticas de Desempenho</h1>
            <div id="stats-general" class="card mb-4"></div>
            <div class="row">
                <div class="col-lg-6">
                    <div id="stats-proficiency" class="card mb-4"></div>
                </div>
                <div class="col-lg-6">
                    <div id="stats-heatmap" class="card mb-4"></div>
                </div>
            </div>
            <div id="stats-details" class="card mb-4"></div>
            <div id="stats-by-table" class="card"></div>
            <div class="text-center mt-4">
                <button class="btn btn-secondary" data-route="home">Voltar ao Menu</button>
            </div>
        </div>
    `,
    formula_quiz_setup: () => `
        <div class="container text-center">
            <h1>Quiz com Fórmulas</h1>
            <div class="mb-3">
                <label for="quiz-config-name" class="form-label">Nome para esta Configuração</label>
                <input type="text" class="form-control" id="quiz-config-name" placeholder="Ex: Treino Quadrado da Soma">
            </div>
            <div class="mb-3">
                <label for="formula-type" class="form-label">Selecione a Fórmula</label>
                <select class="form-select" id="formula-type"></select>
            </div>
            <div id="variable-ranges" class="row mb-3"></div>
            <button class="btn btn-primary" id="save-quiz-config">Salvar Configuração</button>
            <hr>
            <div class="mb-3">
                <label for="saved-quiz-configs" class="form-label">Carregar Configuração Salva</label>
                <select class="form-select" id="saved-quiz-configs"></select>
            </div>
            <button class="btn btn-success" id="start-quiz-with-saved-config">Iniciar Quiz</button>
            <p id="feedback-formula"></p>
            <button class="btn btn-secondary" data-route="home">Voltar ao Menu</button>
        </div>
    `,
    quiz_cronometrado: () => `
        <div class="container text-center">
            <h1>Modo Cronometrado</h1>
            <div class="row">
                <div class="col"><h2 id="score">Pontuação: 0</h2></div>
                <div class="col"><h2 id="timer">Tempo: 60</h2></div>
            </div>
            <h1 id="question-timed"></h1>
            <input type="number" class="form-control" id="answer-timed" placeholder="Sua resposta">
            <p id="feedback-timed"></p>
            <button class="btn btn-primary" id="start-timed-quiz">Iniciar</button>
            <button class="btn btn-secondary" data-route="home" id="back-to-menu-timed" style="display: none;">Voltar ao Menu</button>
        </div>
    `,
    memorizacao: () => `
        <div class="container text-center">
            <h1>Modo Memorização</h1>
            <div id="memorization-content"></div>
            <button class="btn btn-secondary" data-route="home">Voltar ao Menu</button>
        </div>
    `
};

// Funções auxiliares
async function apiCall(func, ...args) {
    try {
        return await window.pywebview.api[func](...args);
    } catch (e) {
        console.error(`Erro ao chamar a API '${func}':`, e);
        // Opcional: Mostrar um erro para o usuário
        const feedbackEl = document.querySelector('#feedback, #feedback-inv, #feedback-formula, #feedback-timed');
        if (feedbackEl) {
            feedbackEl.textContent = "Ocorreu um erro. Tente novamente.";
            feedbackEl.className = 'text-danger';
        }
        return null;
    }
}

function render(template) {
    app.innerHTML = template();
}

function navigateTo(route) {
    app.classList.add('fade-out');
    setTimeout(() => {
        window.location.hash = route;
        app.classList.remove('fade-out');
    }, 300);
}

// Lógica de cada tela
const screenLogics = {
    home: () => {},
    quiz: async () => {
        const questionEl = document.getElementById('question');
        const optionsEl = document.getElementById('options');
        const feedbackEl = document.getElementById('feedback');
        const nextButton = document.getElementById('next-question');

        async function loadQuestion() {
            feedbackEl.textContent = '';
            nextButton.style.display = 'none';
            optionsEl.innerHTML = '<div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div>';

            const questionData = await apiCall('selecionar_proxima_pergunta');
            state.currentQuestion = questionData;
            if (!questionData) {
                questionEl.textContent = 'Parabéns, você completou todas as questões!';
                optionsEl.innerHTML = '';
                return;
            }

            questionEl.textContent = `${questionData.fator1} x ${questionData.fator2} = ?`;
            const options = await apiCall('gerar_opcoes', questionData.fator1, questionData.fator2);
            const correctAnswer = questionData.fator1 * questionData.fator2;

            optionsEl.innerHTML = options.map(opt => `
                <div class="col-6 mb-2">
                    <button class="btn btn-primary w-100 option-btn">${opt}</button>
                </div>
            `).join('');

            const startTime = Date.now();
            optionsEl.querySelectorAll('.option-btn').forEach(button => {
                button.addEventListener('click', () => {
                    const responseTime = (Date.now() - startTime) / 1000;
                    const isCorrect = parseInt(button.textContent) === correctAnswer;
                    apiCall('registrar_resposta', state.currentQuestion, isCorrect, responseTime);

                    feedbackEl.textContent = isCorrect ? 'Correto!' : `Errado! A resposta era ${correctAnswer}`;
                    feedbackEl.className = isCorrect ? 'text-success' : 'text-danger';
                    nextButton.style.display = 'block';
                    optionsEl.querySelectorAll('.option-btn').forEach(btn => btn.disabled = true);
                });
            });
        }

        nextButton.addEventListener('click', loadQuestion);
        loadQuestion();
    },
    treino: async () => {
        const titleEl = document.getElementById('training-title');
        const tableEl = document.getElementById('training-table');
        const checkBtn = document.getElementById('check-answers');
        const summaryEl = document.getElementById('training-summary');

        const suggestedTable = await apiCall('sugerir_tabuada_para_treino');
        if (suggestedTable === null) return;

        titleEl.textContent = `Treinando a Tabuada do ${suggestedTable}`;

        let tableHTML = '<table class="table table-bordered">';
        const inputs = [];
        for (let i = 1; i <= 10; i++) {
            const inputId = `input-${i}`;
            const question = { fator1: suggestedTable, fator2: i };
            inputs.push({ id: inputId, question, correctAnswer: suggestedTable * i });
            tableHTML += `<tr>
                <td>${suggestedTable} x ${i} = </td>
                <td><input type="number" class="form-control" id="${inputId}"></td>
            </tr>`;
        }
        tableHTML += '</table>';
        tableEl.innerHTML = tableHTML;

        checkBtn.addEventListener('click', () => {
            let correctCount = 0;
            inputs.forEach(inputInfo => {
                const inputEl = document.getElementById(inputInfo.id);
                const isCorrect = parseInt(inputEl.value) === inputInfo.correctAnswer;
                apiCall('registrar_resposta', inputInfo.question, isCorrect, null);

                inputEl.classList.add(isCorrect ? 'is-valid' : 'is-invalid');
                if (isCorrect) correctCount++;
                inputEl.disabled = true;
            });
            summaryEl.textContent = `Você acertou ${correctCount} de 10!`;
            checkBtn.disabled = true;
        });
    },
    estatisticas: async () => {
        // Render General Stats
        const generalStatsEl = document.getElementById('stats-general');
        generalStatsEl.innerHTML = '<div class="card-body text-center"><div class="spinner-border" role="status"></div></div>';
        const generalStats = await apiCall('get_estatisticas_gerais');
        if (generalStats) {
            generalStatsEl.innerHTML = `
                <div class="card-header"><h3>Visão Geral</h3></div>
                <div class="card-body">
                    <div class="row text-center">
                        <div class="col-md-3"><h5>Progresso Geral</h5><p>${generalStats.progresso_geral}%</p></div>
                        <div class="col-md-3"><h5>Total de Respostas</h5><p>${generalStats.total_respondidas}</p></div>
                        <div class="col-md-3"><h5>Percentual de Acertos</h5><p>${generalStats.percentual_acertos_geral}%</p></div>
                        <div class="col-md-3"><h5>Tempo Médio de Resposta</h5><p>${generalStats.tempo_medio_resposta_geral}s</p></div>
                    </div>
                </div>
            `;
        }

        // Render Proficiency
        const proficiencyEl = document.getElementById('stats-proficiency');
        proficiencyEl.innerHTML = '<div class="card-body text-center"><div class="spinner-border" role="status"></div></div>';
        const proficiencyData = await apiCall('get_proficiencia_por_tabuada');
        if (proficiencyData) {
            let proficiencyHTML = '<div class="card-header"><h3>Proficiência por Tabuada</h3></div><div class="card-body">';
            for (let i = 1; i <= 10; i++) {
                const proficiency = proficiencyData[i] || 0;
                proficiencyHTML += `
                    <div class="mb-2">
                        <span>Tabuada do ${i}</span>
                        <div class="progress" style="height: 20px;">
                            <div class="progress-bar" role="progressbar" style="width: ${proficiency}%;" aria-valuenow="${proficiency}" aria-valuemin="0" aria-valuemax="100">${proficiency}%</div>
                        </div>
                    </div>`;
            }
            proficiencyHTML += '</div>';
            proficiencyEl.innerHTML = proficiencyHTML;
        }

        // Render Heatmap
        const heatmapEl = document.getElementById('stats-heatmap');
        heatmapEl.innerHTML = '<div class="card-body text-center"><div class="spinner-border" role="status"></div></div>';
        const [heatmapData, minPeso, maxPeso] = await apiCall('gerar_dados_heatmap');
        if (heatmapData) {
            let heatmapHTML = `
                <div class="card-header"><h3>Mapa de Calor de Dificuldade</h3></div>
                <div class="card-body">
                    <table class="table table-bordered heatmap-table">`;
            for (let i = 0; i < 10; i++) {
                heatmapHTML += '<tr>';
                for (let j = 0; j < 10; j++) {
                    const weight = heatmapData[i][j];
                    const normalizedWeight = (weight - minPeso) / (maxPeso - minPeso || 1);
                    const hue = 120 * (1 - normalizedWeight); // Verde (fácil) para Vermelho (difícil)
                    const color = `hsl(${hue}, 85%, 55%)`;
                    heatmapHTML += `<td style="background-color: ${color};" title="Dificuldade de ${i+1}x${j+1}: ${weight.toFixed(1)}"></td>`;
                }
                heatmapHTML += '</tr>';
            }
            heatmapHTML += '</table></div>';
            heatmapEl.innerHTML = heatmapHTML;
        }

        // Render Detailed Stats
        const detailsEl = document.getElementById('stats-details');
        detailsEl.innerHTML = '<div class="card-body text-center"><div class="spinner-border" role="status"></div></div>';
        const detailedStats = await apiCall('get_estatisticas_detalhadas');
        if (detailedStats) {
            const renderList = (title, items) => `
                <div class="col-md-3">
                    <h5>${title}</h5>
                    <ul class="list-group">${items.map(item => `<li class="list-group-item">${item}</li>`).join('') || '<li class="list-group-item">N/A</li>'}</ul>
                </div>`;
            detailsEl.innerHTML = `
                <div class="card-header"><h3>Destaques</h3></div>
                <div class="card-body">
                    <div class="row">
                        ${renderList('Mais Difíceis', detailedStats.top_3_dificeis)}
                        ${renderList('Mais Fáceis', detailedStats.top_3_faceis)}
                        ${renderList('Mais Lentas', detailedStats.top_3_lentas)}
                        ${renderList('Mais Rápidas', detailedStats.top_3_rapidas)}
                    </div>
                </div>
            `;
        }

        // Render Stats by Table
        const byTableEl = document.getElementById('stats-by-table');
        byTableEl.innerHTML = '<div class="card-body text-center"><div class="spinner-border" role="status"></div></div>';
        const tableStats = await apiCall('get_estatisticas_por_tabuada');
        if (tableStats) {
            let tableHTML = `
                <div class="card-header"><h3>Desempenho por Tabuada</h3></div>
                <div class="card-body">
                    <table class="table table-striped table-hover">
                        <thead><tr><th>Tabuada</th><th>% Acertos</th><th>Tempo Médio (s)</th><th>Total de Respostas</th></tr></thead>
                        <tbody>`;
            for (let i = 1; i <= 10; i++) {
                const stats = tableStats[i];
                tableHTML += `
                    <tr>
                        <td>Tabuada do ${i}</td>
                        <td>${stats.percentual_acertos}%</td>
                        <td>${stats.tempo_medio}s</td>
                        <td>${stats.total_respostas}</td>
                    </tr>`;
            }
            tableHTML += '</tbody></table></div>';
            byTableEl.innerHTML = tableHTML;
        }
    },
    // Adicionar lógicas para as outras telas...
};

// Router
function router() {
    const route = window.location.hash.substring(1) || 'home';
    state.currentRoute = route;

    const template = templates[route] || templates['home'];
    render(template);

    const logic = screenLogics[route] || (() => {});
    logic();
}

// Event Listeners
document.addEventListener('click', e => {
    if (e.target.matches('[data-route]')) {
        e.preventDefault();
        navigateTo(e.target.dataset.route);
    }
});

themeToggle.addEventListener('click', () => {
    const newTheme = body.className === 'light-theme' ? 'dark-theme' : 'light-theme';
    setTheme(newTheme);
});

async function setTheme(theme) {
    body.className = theme;
    themeToggle.textContent = theme === 'dark-theme' ? '☀️' : '🌙';
    state.theme = theme;
    await apiCall('salvar_tema', theme);
}

// Inicialização
window.addEventListener('hashchange', router);
window.addEventListener('load', async () => {
    document.getElementById('intro').style.display = 'flex';

    const initialData = await apiCall('load_initial_data');
    if (initialData) {
        setTheme(initialData.tema_ativo || 'light-theme');
    }

    setTimeout(() => {
        document.getElementById('intro').style.display = 'none';
        document.getElementById('app').style.display = 'block';
        router();
    }, 2000);
});
