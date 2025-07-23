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
    quiz_invertido: async () => {
        const questionEl = document.getElementById('question-inv');
        const optionsEl = document.getElementById('options-inv');
        const feedbackEl = document.getElementById('feedback-inv');
        const nextButton = document.getElementById('next-question-inv');

        async function loadQuestion() {
            feedbackEl.textContent = '';
            nextButton.style.display = 'none';
            optionsEl.innerHTML = '<div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div>';

            const questionData = await apiCall('selecionar_proxima_pergunta_invertida');
            state.currentQuestion = questionData;
            if (!questionData) {
                questionEl.textContent = 'Parabéns, você completou todas as questões!';
                optionsEl.innerHTML = '';
                return;
            }

            questionEl.textContent = `? x ? = ${questionData.resultado}`;
            const options = await apiCall('gerar_opcoes_invertidas', questionData.resultado);
            const correctAnswer = `${questionData.fator1} x ${questionData.fator2}`;

            optionsEl.innerHTML = options.map(opt => `
                <div class="col-6 mb-2">
                    <button class="btn btn-primary w-100 option-btn">${opt.fator1} x ${opt.fator2}</button>
                </div>
            `).join('');

            const startTime = Date.now();
            optionsEl.querySelectorAll('.option-btn').forEach(button => {
                button.addEventListener('click', () => {
                    const responseTime = (Date.now() - startTime) / 1000;
                    const isCorrect = button.textContent.trim() === correctAnswer;
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
    quiz_cronometrado: () => {
        const scoreEl = document.getElementById('score');
        const timerEl = document.getElementById('timer');
        const questionEl = document.getElementById('question-timed');
        const answerInput = document.getElementById('answer-timed');
        const feedbackEl = document.getElementById('feedback-timed');
        const startButton = document.getElementById('start-timed-quiz');
        const backToMenuButton = document.getElementById('back-to-menu-timed');

        function resetQuiz() {
            state.timedQuiz.score = 0;
            state.timedQuiz.timeLeft = 60;
            state.timedQuiz.isActive = false;
            if (state.timedQuiz.timer) clearInterval(state.timedQuiz.timer);

            scoreEl.textContent = 'Pontuação: 0';
            timerEl.textContent = 'Tempo: 60';
            questionEl.textContent = 'Pressione Iniciar para começar';
            answerInput.value = '';
            answerInput.disabled = true;
            feedbackEl.textContent = '';
            startButton.style.display = 'block';
            backToMenuButton.style.display = 'none';
        }

        async function nextQuestion() {
            const questionData = await apiCall('selecionar_proxima_pergunta');
            state.currentQuestion = questionData;
            if (!questionData) {
                endQuiz();
                return;
            }
            questionEl.textContent = `${questionData.fator1} x ${questionData.fator2} = ?`;
            answerInput.value = '';
            answerInput.focus();
        }

        function endQuiz() {
            state.timedQuiz.isActive = false;
            clearInterval(state.timedQuiz.timer);
            questionEl.textContent = `Tempo esgotado! Pontuação final: ${state.timedQuiz.score}`;
            answerInput.disabled = true;
            startButton.style.display = 'none';
            backToMenuButton.style.display = 'block';
            apiCall('registrar_pontuacao_cronometrada', state.timedQuiz.score);
        }

        function handleAnswer(e) {
            if (e.key === 'Enter' && state.timedQuiz.isActive) {
                const userAnswer = parseInt(answerInput.value);
                const correctAnswer = state.currentQuestion.fator1 * state.currentQuestion.fator2;
                const isCorrect = userAnswer === correctAnswer;

                if (isCorrect) {
                    state.timedQuiz.score++;
                    scoreEl.textContent = `Pontuação: ${state.timedQuiz.score}`;
                    feedbackEl.textContent = 'Correto!';
                    feedbackEl.className = 'text-success';
                } else {
                    feedbackEl.textContent = `Errado! A resposta era ${correctAnswer}`;
                    feedbackEl.className = 'text-danger';
                }
                apiCall('registrar_resposta', state.currentQuestion, isCorrect, null);
                setTimeout(() => {
                    feedbackEl.textContent = '';
                    nextQuestion();
                }, 1000);
            }
        }

        startButton.addEventListener('click', () => {
            resetQuiz();
            state.timedQuiz.isActive = true;
            answerInput.disabled = false;
            startButton.style.display = 'none';
            backToMenuButton.style.display = 'none';

            state.timedQuiz.timer = setInterval(() => {
                state.timedQuiz.timeLeft--;
                timerEl.textContent = `Tempo: ${state.timedQuiz.timeLeft}`;
                if (state.timedQuiz.timeLeft <= 0) {
                    endQuiz();
                }
            }, 1000);

            nextQuestion();
        });

        answerInput.addEventListener('keyup', handleAnswer);
        resetQuiz();
    },
    memorizacao: () => {
        const contentEl = document.getElementById('memorization-content');
        let state = {
            stage: 'selection', // selection, memorization, test
            tableNumber: null,
            questions: [],
            currentQuestionIndex: 0,
            correctAnswers: 0,
        };

        function renderSelection() {
            let buttonsHTML = '<h2>Qual tabuada você quer memorizar?</h2><div class="d-grid gap-2 col-6 mx-auto">';
            for (let i = 1; i <= 10; i++) {
                buttonsHTML += `<button class="btn btn-primary select-table-btn" data-table="${i}">Tabuada do ${i}</button>`;
            }
            buttonsHTML += '</div>';
            contentEl.innerHTML = buttonsHTML;

            contentEl.querySelectorAll('.select-table-btn').forEach(button => {
                button.addEventListener('click', (e) => {
                    state.tableNumber = parseInt(e.target.dataset.table);
                    state.stage = 'memorization';
                    renderMemorization();
                });
            });
        }

        function renderMemorization() {
            let tableHTML = `<h2>Memorize a Tabuada do ${state.tableNumber}</h2><table class="table">`;
            for (let i = 1; i <= 10; i++) {
                tableHTML += `<tr><td>${state.tableNumber} x ${i}</td><td>=</td><td>${state.tableNumber * i}</td></tr>`;
            }
            tableHTML += '</table><button class="btn btn-primary" id="start-test-btn">Iniciar Teste</button>';
            contentEl.innerHTML = tableHTML;

            document.getElementById('start-test-btn').addEventListener('click', () => {
                state.stage = 'test';
                generateTestQuestions();
                renderTest();
            });
        }

        function generateTestQuestions() {
            state.questions = [];
            for (let i = 1; i <= 10; i++) {
                state.questions.push({ fator1: state.tableNumber, fator2: i, answer: state.tableNumber * i });
            }
            // Shuffle questions
            state.questions.sort(() => Math.random() - 0.5);
            state.currentQuestionIndex = 0;
            state.correctAnswers = 0;
        }

        function renderTest() {
            if (state.currentQuestionIndex >= state.questions.length) {
                renderTestResults();
                return;
            }

            const question = state.questions[state.currentQuestionIndex];
            const questionText = `${question.fator1} x ${question.fator2} = ?`;
            contentEl.innerHTML = `
                <h2>Teste de Memorização</h2>
                <h3>${questionText}</h3>
                <input type="number" class="form-control w-50 mx-auto" id="memorization-answer">
                <button class="btn btn-primary mt-3" id="submit-answer-btn">Responder</button>
                <p id="feedback-memorization" class="mt-2"></p>
                <div class="progress mt-3" style="height: 20px;">
                    <div class="progress-bar" role="progressbar" style="width: ${state.currentQuestionIndex / state.questions.length * 100}%;" aria-valuenow="${state.currentQuestionIndex}" aria-valuemin="0" aria-valuemax="${state.questions.length}"></div>
                </div>
            `;

            const answerInput = document.getElementById('memorization-answer');
            const submitBtn = document.getElementById('submit-answer-btn');
            const feedbackEl = document.getElementById('feedback-memorization');

            const submitAnswer = () => {
                const userAnswer = parseInt(answerInput.value);
                const isCorrect = userAnswer === question.answer;

                if (isCorrect) {
                    state.correctAnswers++;
                    feedbackEl.textContent = 'Correto!';
                    feedbackEl.className = 'text-success';
                } else {
                    feedbackEl.textContent = `Errado. A resposta é ${question.answer}.`;
                    feedbackEl.className = 'text-danger';
                }

                apiCall('registrar_resposta', {fator1: question.fator1, fator2: question.fator2}, isCorrect, null, 'memorizacao');

                submitBtn.disabled = true;
                answerInput.disabled = true;

                setTimeout(() => {
                    state.currentQuestionIndex++;
                    renderTest();
                }, 1500);
            };

            submitBtn.addEventListener('click', submitAnswer);
            answerInput.addEventListener('keyup', (e) => {
                if (e.key === 'Enter') {
                    submitAnswer();
                }
            });
            answerInput.focus();
        }

        function renderTestResults() {
            const accuracy = (state.correctAnswers / state.questions.length) * 100;
            contentEl.innerHTML = `
                <h2>Resultado do Teste</h2>
                <p>Você acertou ${state.correctAnswers} de ${state.questions.length} questões.</p>
                <p>Sua precisão foi de ${accuracy.toFixed(0)}%.</p>
                <button class="btn btn-primary" id="restart-memorization-btn">Tentar Novamente</button>
            `;
            document.getElementById('restart-memorization-btn').addEventListener('click', renderSelection);
        }

        renderSelection();
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
