// Estado da aplicação
const state = {
    currentQuestion: null,
    currentRoute: '',
    theme: 'light-theme',
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

function render(templateName) {
    const template = document.querySelector(`template[data-template="${templateName}"]`);
    if (template) {
        app.innerHTML = template.innerHTML;
    } else {
        console.error(`Template "${templateName}" não encontrado.`);
        app.innerHTML = `<div class="alert alert-danger">Erro: Template ${templateName} não encontrado.</div>`;
    }
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
    memorizacao: () => {
        const contentEl = document.getElementById('memorization-content');
        let localState = {
            tableNumber: null,
            // Fase de Codificação
            encodingStep: 1, // De 1 a 10
            // Fase de Teste
            questions: [],
            currentQuestionIndex: 0,
            errorStack: [], // Pilha de erros para re-teste
            isReTest: false // Flag para saber se a pergunta atual é um re-teste
        };

        async function start() {
            contentEl.innerHTML = '<div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div>';
            const tableToMemorize = await apiCall('sugerir_tabuada_para_memorizacao');
            if (tableToMemorize === null) {
                contentEl.innerHTML = '<p>Ocorreu um erro ao sugerir uma tabuada. Tente novamente.</p>';
                return;
            }
            localState.tableNumber = tableToMemorize;
            localState.encodingStep = 1;
            showNextEncodingStep();
        }

        function showNextEncodingStep() {
            if (localState.encodingStep > 10) {
                startTestPhase();
                return;
            }

            const fator1 = localState.tableNumber;
            const fator2 = localState.encodingStep;
            const result = fator1 * fator2;

            contentEl.innerHTML = `
                <div class="text-center">
                    <h2>Fase de Codificação: Tabuada do ${fator1}</h2>
                    <p class="lead">Digite o resultado correto para avançar.</p>
                    <div class="my-4">
                        <span class="h3">${fator1} x ${fator2} =</span>
                        <input type="number" class="form-control form-control-lg d-inline-block w-25 ms-2" id="encoding-input" autofocus>
                    </div>
                    <p id="feedback-encoding" class="mt-2" style="height: 24px;"></p>
                </div>
            `;

            const input = document.getElementById('encoding-input');
            input.addEventListener('keyup', (e) => handleEncodingInput(e, result));
            input.focus();
        }

        function handleEncodingInput(event, correctResult) {
            const feedbackEl = document.getElementById('feedback-encoding');
            if (event.key !== 'Enter') return;

            const input = event.target;
            const userAnswer = parseInt(input.value);

            if (userAnswer === correctResult) {
                localState.encodingStep++;
                showNextEncodingStep();
            } else {
                feedbackEl.textContent = 'Tente de novo.';
                feedbackEl.className = 'text-danger';
                input.value = '';
                // Animação de erro para feedback visual
                input.classList.add('is-invalid');
                setTimeout(() => {
                    input.classList.remove('is-invalid');
                    feedbackEl.textContent = '';
                }, 1000);
            }
        }

        function startTestPhase() {
            generateQuestions();
            askQuestion();
        }

        function generateQuestions() {
            localState.questions = [];
            for (let i = 1; i <= 10; i++) {
                localState.questions.push({ fator1: localState.tableNumber, fator2: i, answer: localState.tableNumber * i });
            }
            localState.questions.sort(() => Math.random() - 0.5); // Embaralha as questões
            localState.currentQuestionIndex = 0;
            localState.errorStack = [];
        }

        function askQuestion() {
            // Condição de término: ambas as listas estão vazias
            if (localState.currentQuestionIndex >= localState.questions.length && localState.errorStack.length === 0) {
                contentEl.innerHTML = `
                    <h2>Parabéns!</h2>
                    <p>Você dominou a tabuada do ${localState.tableNumber}!</p>
                    <p>Continue praticando para se tornar um mestre!</p>
                    <button class="btn btn-primary mt-3" id="next-table-btn">Memorizar Outra Tabuada</button>
                `;
                document.getElementById('next-table-btn').addEventListener('click', start);
                return;
            }

            let question;
            localState.isReTest = false;

            // Decide se pega uma questão da pilha de erros ou da lista principal
            const shouldPickFromErrorStack = localState.errorStack.length > 0 && Math.random() < 0.7;

            if (shouldPickFromErrorStack) {
                question = localState.errorStack.shift(); // Pega o primeiro erro da fila
                localState.isReTest = true;
            } else if (localState.currentQuestionIndex < localState.questions.length) {
                question = localState.questions[localState.currentQuestionIndex];
                localState.currentQuestionIndex++;
            } else {
                 // Caso a lista principal tenha acabado mas a pilha de erros ainda não
                question = localState.errorStack.shift();
                localState.isReTest = true;
            }


            const questionText = `${question.fator1} x ${question.fator2} = ?`;
            contentEl.innerHTML = `
                <h2>Teste de Memorização</h2>
                <h3 class="my-4">${questionText}</h3>
                <input type="number" class="form-control w-50 mx-auto" id="memorization-answer" autofocus>
                <button class="btn btn-primary mt-3" id="submit-answer-btn">Responder</button>
                <p id="feedback-memorization" class="mt-2" style="height: 24px;"></p>
            `;

            const answerInput = document.getElementById('memorization-answer');
            const submitBtn = document.getElementById('submit-answer-btn');

            const submitAnswer = () => {
                const userAnswer = parseInt(answerInput.value);
                const isCorrect = userAnswer === question.answer;

                // Registra a resposta com o modo 'memorizacao'
                apiCall('registrar_resposta', {fator1: question.fator1, fator2: question.fator2}, isCorrect, null, 'memorizacao');
                submitBtn.disabled = true;
                answerInput.disabled = true;

                const feedbackEl = document.getElementById('feedback-memorization');
                if (isCorrect) {
                    feedbackEl.textContent = 'Correto!';
                    feedbackEl.className = 'text-success';
                    // Se era um re-teste e acertou, a pergunta é removida permanentemente.
                    // Se não, ela simplesmente não é adicionada à pilha de erros.
                } else {
                    feedbackEl.textContent = `Errado. A resposta é ${question.answer}.`;
                    feedbackEl.className = 'text-danger';
                    // Adiciona a pergunta errada no final da pilha para ser re-testada
                    localState.errorStack.push(question);
                }
                setTimeout(askQuestion, 1500); // Passa para a próxima pergunta
            };

            submitBtn.addEventListener('click', submitAnswer);
            answerInput.addEventListener('keyup', (e) => {
                if (e.key === 'Enter') submitAnswer();
            });
            answerInput.focus();
        }

        // Inicia o fluxo
        start();
    },
};

// Router
function router() {
    const route = window.location.hash.substring(1) || 'home';
    state.currentRoute = route;

    render(route);

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
