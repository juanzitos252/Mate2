const app = document.getElementById('app');

function renderPresentationScreen() {
    app.innerHTML = `
        <div class="container text-center">
            <h1>Quiz Mestre da Tabuada</h1>
            <p>Aprenda e memorize a tabuada de forma divertida e adaptativa!</p>
            <div class="d-grid gap-2 col-6 mx-auto">
                <button class="btn btn-primary" onclick="navigateTo('quiz')">Iniciar Quiz</button>
                <button class="btn btn-secondary" onclick="navigateTo('quiz_invertido')">Quiz Invertido</button>
                <button class="btn btn-primary" onclick="navigateTo('treino')">Modo Treino</button>
                <button class="btn btn-info" onclick="navigateTo('estatisticas')">Estatísticas</button>
                <button class="btn btn-secondary" onclick="navigateTo('formula_quiz_setup')">Quiz com Fórmulas</button>
                <button class="btn btn-primary" onclick="navigateTo('quiz_cronometrado')">Modo Cronometrado</button>
            </div>
        </div>
    `;
}

function renderQuizScreen() {
    app.innerHTML = `
        <div class="container text-center">
            <h1 id="question"></h1>
            <div class="row">
                <div class="col-md-6">
                    <button class="btn btn-primary w-100 mb-2" id="option1"></button>
                </div>
                <div class="col-md-6">
                    <button class="btn btn-primary w-100 mb-2" id="option2"></button>
                </div>
            </div>
            <div class="row">
                <div class="col-md-6">
                    <button class="btn btn-primary w-100 mb-2" id="option3"></button>
                </div>
                <div class="col-md-6">
                    <button class="btn btn-primary w-100 mb-2" id="option4"></button>
                </div>
            </div>
            <p id="feedback"></p>
            <button class="btn btn-secondary" id="next-question" style="display: none;">Próxima Pergunta</button>
            <button class="btn btn-secondary" onclick="navigateTo('home')">Voltar ao Menu</button>
        </div>
    `;
    loadQuizQuestion();
}

function renderQuizInvertidoScreen() {
    app.innerHTML = `
        <div class="container text-center">
            <h1 id="question-inv"></h1>
            <div class="row">
                <div class="col-md-6">
                    <button class="btn btn-primary w-100 mb-2" id="option1-inv"></button>
                </div>
                <div class="col-md-6">
                    <button class="btn btn-primary w-100 mb-2" id="option2-inv"></button>
                </div>
            </div>
            <div class="row">
                <div class="col-md-6">
                    <button class="btn btn-primary w-100 mb-2" id="option3-inv"></button>
                </div>
                <div class="col-md-6">
                    <button class="btn btn-primary w-100 mb-2" id="option4-inv"></button>
                </div>
            </div>
            <p id="feedback-inv"></p>
            <button class="btn btn-secondary" id="next-question-inv" style="display: none;">Próxima Pergunta</button>
            <button class="btn btn-secondary" onclick="navigateTo('home')">Voltar ao Menu</button>
        </div>
    `;
    loadQuizInvertidoQuestion();
}

function renderTreinoScreen() {
    app.innerHTML = `
        <div class="container text-center">
            <h1>Modo Treino</h1>
            <h2 id="training-title"></h2>
            <div id="training-table"></div>
            <button class="btn btn-primary" id="check-answers">Verificar Respostas</button>
            <p id="training-summary"></p>
            <button class="btn btn-secondary" onclick="navigateTo('home')">Voltar ao Menu</button>
        </div>
    `;
    loadTrainingTable();
}

function renderEstatisticasScreen() {
    app.innerHTML = `
        <div class="container text-center">
            <h1>Estatísticas</h1>
            <div id="stats-summary"></div>
            <div id="heatmap"></div>
            <div id="proficiency"></div>
            <div id="top-difficulties"></div>
            <button class="btn btn-secondary" onclick="navigateTo('home')">Voltar ao Menu</button>
        </div>
    `;
    loadStatistics();
}

function renderFormulaQuizSetupScreen() {
    app.innerHTML = `
        <div class="container text-center">
            <h1>Quiz com Fórmulas</h1>
            <div class="mb-3">
                <label for="quiz-config-name" class="form-label">Nome para esta Configuração de Quiz</label>
                <input type="text" class="form-control" id="quiz-config-name" placeholder="Ex: Treino Quadrado da Soma">
            </div>
            <div class="mb-3">
                <label for="formula-type" class="form-label">Selecione o Tipo de Fórmula</label>
                <select class="form-select" id="formula-type"></select>
            </div>
            <div class="row mb-3">
                <div class="col">
                    <label for="var-a-range" class="form-label">Range para 'a' (1-10)</label>
                    <input type="text" class="form-control" id="var-a-range" value="1-10">
                </div>
                <div class="col">
                    <label for="var-b-range" class="form-label">Range para 'b' (1-10)</label>
                    <input type="text" class="form-control" id="var-b-range" value="1-10">
                </div>
            </div>
            <button class="btn btn-primary" id="save-quiz-config">Salvar Configuração do Quiz</button>
            <hr>
            <div class="mb-3">
                <label for="saved-quiz-configs" class="form-label">Ou selecione uma configuração de quiz salva</label>
                <select class="form-select" id="saved-quiz-configs"></select>
            </div>
            <button class="btn btn-success" id="start-quiz-with-saved-config">Iniciar Quiz com Config. Salva</button>
            <p id="feedback-formula"></p>
            <button class="btn btn-secondary" onclick="navigateTo('home')">Voltar ao Menu</button>
        </div>
    `;
    loadFormulaQuizSetup();
}

function renderQuizCronometradoScreen() {
    app.innerHTML = `
        <div class="container text-center">
            <h1>Modo Cronometrado</h1>
            <div class="row">
                <div class="col">
                    <h2 id="score">Pontuação: 0</h2>
                </div>
                <div class="col">
                    <h2 id="timer">Tempo: 60</h2>
                </div>
            </div>
            <h1 id="question-timed"></h1>
            <input type="text" class="form-control" id="answer-timed" placeholder="Sua resposta">
            <p id="feedback-timed"></p>
            <button class="btn btn-primary" id="start-timed-quiz">Iniciar Quiz Cronometrado</button>
            <button class="btn btn-secondary" onclick="navigateTo('home')">Voltar ao Menu</button>
        </div>
    `;
    loadTimedQuiz();
}

const routes = {
    '': renderPresentationScreen,
    'home': renderPresentationScreen,
    'quiz': renderQuizScreen,
    'quiz_invertido': renderQuizInvertidoScreen,
    'treino': renderTreinoScreen,
    'estatisticas': renderEstatisticasScreen,
    'formula_quiz_setup': renderFormulaQuizSetupScreen,
    'quiz_cronometrado': renderQuizCronometradoScreen,
};

function navigateTo(route) {
    location.hash = route;
}

function router() {
    const route = location.hash.substring(1) || '';
    const renderFunction = routes[route] || renderPresentationScreen;
    renderFunction();
}

async function loadQuizQuestion() {
    const questionEl = document.getElementById('question');
    const option1El = document.getElementById('option1');
    const option2El = document.getElementById('option2');
    const option3El = document.getElementById('option3');
    const option4El = document.getElementById('option4');
    const feedbackEl = document.getElementById('feedback');
    const nextQuestionEl = document.getElementById('next-question');

    feedbackEl.textContent = '';
    nextQuestionEl.style.display = 'none';

    const questionData = await window.pywebview.api.selecionar_proxima_pergunta();
    if (!questionData) {
        questionEl.textContent = 'Parabéns, você completou o quiz!';
        option1El.style.display = 'none';
        option2El.style.display = 'none';
        option3El.style.display = 'none';
        option4El.style.display = 'none';
        return;
    }

    questionEl.textContent = `${questionData.fator1} x ${questionData.fator2} = ?`;
    const correctAnswer = questionData.fator1 * questionData.fator2;
    const options = await window.pywebview.api.gerar_opcoes(questionData.fator1, questionData.fator2);

    const buttons = [option1El, option2El, option3El, option4El];
    buttons.forEach((button, index) => {
        button.textContent = options[index];
        button.onclick = () => {
            const isCorrect = parseInt(button.textContent) === correctAnswer;
            window.pywebview.api.registrar_resposta(questionData, isCorrect);
            feedbackEl.textContent = isCorrect ? 'Correto!' : `Errado! A resposta era ${correctAnswer}`;
            nextQuestionEl.style.display = 'block';
            buttons.forEach(btn => btn.disabled = true);
        };
        button.disabled = false;
    });

    nextQuestionEl.onclick = loadQuizQuestion;
}

async function loadQuizInvertidoQuestion() {
    const questionEl = document.getElementById('question-inv');
    const option1El = document.getElementById('option1-inv');
    const option2El = document.getElementById('option2-inv');
    const option3El = document.getElementById('option3-inv');
    const option4El = document.getElementById('option4-inv');
    const feedbackEl = document.getElementById('feedback-inv');
    const nextQuestionEl = document.getElementById('next-question-inv');

    feedbackEl.textContent = '';
    nextQuestionEl.style.display = 'none';

    const questionData = await window.pywebview.api.selecionar_proxima_pergunta();
    if (!questionData) {
        questionEl.textContent = 'Parabéns, você completou o quiz!';
        option1El.style.display = 'none';
        option2El.style.display = 'none';
        option3El.style.display = 'none';
        option4El.style.display = 'none';
        return;
    }

    const result = questionData.fator1 * questionData.fator2;
    questionEl.textContent = `Qual operação resulta em ${result}?`;
    const correctAnswer = `${questionData.fator1} x ${questionData.fator2}`;
    const options = await window.pywebview.api.gerar_opcoes_quiz_invertido(questionData);

    const buttons = [option1El, option2El, option3El, option4El];
    buttons.forEach((button, index) => {
        button.textContent = options[index].texto;
        button.onclick = () => {
            const isCorrect = button.textContent === correctAnswer;
            window.pywebview.api.registrar_resposta(questionData, isCorrect);
            feedbackEl.textContent = isCorrect ? 'Correto!' : `Errado! A resposta era ${correctAnswer}`;
            nextQuestionEl.style.display = 'block';
            buttons.forEach(btn => btn.disabled = true);
        };
        button.disabled = false;
    });

    nextQuestionEl.onclick = loadQuizInvertidoQuestion;
}

async function loadTrainingTable() {
    const trainingTitleEl = document.getElementById('training-title');
    const trainingTableEl = document.getElementById('training-table');
    const checkAnswersEl = document.getElementById('check-answers');
    const trainingSummaryEl = document.getElementById('training-summary');

    const suggestedTable = await window.pywebview.api.sugerir_tabuada_para_treino();
    trainingTitleEl.textContent = `Treinando a Tabuada do ${suggestedTable}`;

    let tableHTML = '<table class="table table-bordered">';
    const inputs = [];
    for (let i = 1; i <= 10; i++) {
        const inputId = `input-${i}`;
        inputs.push({ id: inputId, fator1: suggestedTable, fator2: i, correctAnswer: suggestedTable * i });
        tableHTML += `
            <tr>
                <td>${suggestedTable} x ${i} = </td>
                <td><input type="number" class="form-control" id="${inputId}"></td>
            </tr>
        `;
    }
    tableHTML += '</table>';
    trainingTableEl.innerHTML = tableHTML;

    checkAnswersEl.onclick = () => {
        let correctAnswers = 0;
        inputs.forEach(input => {
            const inputEl = document.getElementById(input.id);
            const isCorrect = parseInt(inputEl.value) === input.correctAnswer;
            if (isCorrect) {
                correctAnswers++;
                inputEl.classList.add('is-valid');
            } else {
                inputEl.classList.add('is-invalid');
            }
            inputEl.disabled = true;
            window.pywebview.api.registrar_resposta({ fator1: input.fator1, fator2: input.fator2 }, isCorrect);
        });
        trainingSummaryEl.textContent = `Você acertou ${correctAnswers} de 10!`;
        checkAnswersEl.disabled = true;
    };
}

async function loadStatistics() {
    const statsSummaryEl = document.getElementById('stats-summary');
    const heatmapEl = document.getElementById('heatmap');
    const proficiencyEl = document.getElementById('proficiency');
    const topDifficultiesEl = document.getElementById('top-difficulties');

    const stats = await window.pywebview.api.calcular_estatisticas_gerais();
    statsSummaryEl.innerHTML = `
        <p>Total de Perguntas Respondidas: ${stats.total_respondidas}</p>
        <p>Percentual de Acertos Geral: ${stats.percentual_acertos_geral}%</p>
    `;

    const heatmapData = await window.pywebview.api.gerar_dados_heatmap();
    let heatmapHTML = '<h2>Mapa de Calor da Tabuada</h2><table class="table table-bordered">';
    for (let i = 0; i < 10; i++) {
        heatmapHTML += '<tr>';
        for (let j = 0; j < 10; j++) {
            const weight = heatmapData[i][j];
            const color = `hsl(${120 - weight * 12}, 100%, 50%)`;
            heatmapHTML += `<td style="background-color: ${color};">${weight.toFixed(1)}</td>`;
        }
        heatmapHTML += '</tr>';
    }
    heatmapHTML += '</table>';
    heatmapEl.innerHTML = heatmapHTML;

    const proficiencyData = await window.pywebview.api.calcular_proficiencia_tabuadas();
    let proficiencyHTML = '<h2>Proficiência por Tabuada</h2>';
    for (let i = 1; i <= 10; i++) {
        proficiencyHTML += `
            <p>Tabuada do ${i}: ${proficiencyData[i].toFixed(1)}%</p>
            <div class="progress">
                <div class="progress-bar" role="progressbar" style="width: ${proficiencyData[i]}%;" aria-valuenow="${proficiencyData[i]}" aria-valuemin="0" aria-valuemax="100"></div>
            </div>
        `;
    }
    proficiencyEl.innerHTML = proficiencyHTML;

    let topDifficultiesHTML = '<h2>Maiores Dificuldades Atuais</h2>';
    stats.top_3_dificeis.forEach(item => {
        topDifficultiesHTML += `<p>${item}</p>`;
    });
    topDifficultiesEl.innerHTML = topDifficultiesHTML;
}

async function loadFormulaQuizSetup() {
    const formulaTypeEl = document.getElementById('formula-type');
    const savedQuizConfigsEl = document.getElementById('saved-quiz-configs');
    const saveQuizConfigEl = document.getElementById('save-quiz-config');
    const startQuizWithSavedConfigEl = document.getElementById('start-quiz-with-saved-config');
    const feedbackFormulaEl = document.getElementById('feedback-formula');
    const quizConfigNameEl = document.getElementById('quiz-config-name');
    const varARangeEl = document.getElementById('var-a-range');
    const varBRangeEl = document.getElementById('var-b-range');

    const formulaTypes = await window.pywebview.api.get_formula_definitions();
    formulaTypes.forEach(formula => {
        const option = document.createElement('option');
        option.value = formula.id;
        option.textContent = formula.display_name;
        formulaTypeEl.appendChild(option);
    });

    async function loadSavedConfigs() {
        savedQuizConfigsEl.innerHTML = '';
        const savedConfigs = await window.pywebview.api.get_saved_quiz_configs();
        savedConfigs.forEach(config => {
            const option = document.createElement('option');
            option.value = config.name;
            option.textContent = config.name;
            savedQuizConfigsEl.appendChild(option);
        });
    }

    saveQuizConfigEl.onclick = async () => {
        const config = {
            name: quizConfigNameEl.value,
            formula_id: formulaTypeEl.value,
            ranges: {
                a: varARangeEl.value,
                b: varBRangeEl.value,
            }
        };
        await window.pywebview.api.save_quiz_config(config);
        feedbackFormulaEl.textContent = 'Configuração salva com sucesso!';
        loadSavedConfigs();
    };

    startQuizWithSavedConfigEl.onclick = async () => {
        const configName = savedQuizConfigsEl.value;
        await window.pywebview.api.set_current_custom_formula_for_quiz(configName);
        navigateTo('custom_quiz');
    };

    loadSavedConfigs();
}

async function loadTimedQuiz() {
    const scoreEl = document.getElementById('score');
    const timerEl = document.getElementById('timer');
    const questionEl = document.getElementById('question-timed');
    const answerEl = document.getElementById('answer-timed');
    const feedbackEl = document.getElementById('feedback-timed');
    const startButton = document.getElementById('start-timed-quiz');

    let score = 0;
    let timeLeft = 60;
    let timer;
    let currentQuestion;

    async function nextQuestion() {
        currentQuestion = await window.pywebview.api.selecionar_proxima_pergunta();
        if (currentQuestion) {
            questionEl.textContent = `${currentQuestion.fator1} x ${currentQuestion.fator2} = ?`;
            answerEl.value = '';
            answerEl.focus();
        } else {
            endGame();
        }
    }

    function checkAnswer() {
        if (!currentQuestion) return;
        const correctAnswer = currentQuestion.fator1 * currentQuestion.fator2;
        if (parseInt(answerEl.value) === correctAnswer) {
            score++;
            scoreEl.textContent = `Pontuação: ${score}`;
            feedbackEl.textContent = 'Correto!';
        } else {
            feedbackEl.textContent = `Errado! A resposta era ${correctAnswer}`;
        }
        nextQuestion();
    }

    function endGame() {
        clearInterval(timer);
        questionEl.textContent = 'Tempo Esgotado!';
        answerEl.disabled = true;
        feedbackEl.textContent = `Pontuação Final: ${score}`;
        window.pywebview.api.save_timed_mode_score(score);
    }

    function countdown() {
        timeLeft--;
        timerEl.textContent = `Tempo: ${timeLeft}`;
        if (timeLeft === 0) {
            endGame();
        }
    }

    startButton.onclick = () => {
        score = 0;
        timeLeft = 60;
        scoreEl.textContent = `Pontuação: ${score}`;
        timerEl.textContent = `Tempo: ${timeLeft}`;
        answerEl.disabled = false;
        startButton.style.display = 'none';
        timer = setInterval(countdown, 1000);
        nextQuestion();
    };

    answerEl.onkeyup = (e) => {
        if (e.key === 'Enter') {
            checkAnswer();
        }
    };
}

window.addEventListener('hashchange', router);
window.addEventListener('load',router);
