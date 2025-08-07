
let tempo = parseInt("{{ tempo }}"); // Recebe do Flask
let timerElement = document.getElementById('timer');
let progressBar = document.getElementById('progress-bar');

let tempoInicial = tempo;

let countdown = setInterval(() => {
    tempo--;
    timerElement.textContent = tempo;

    // Atualiza barra de progresso
    let percent = (tempo / tempoInicial) * 100;
    progressBar.style.width = percent + "%";

    // Efeitos visuais
    timerElement.classList.remove("time-warning", "time-danger");
    if (tempo <= 10 && tempo > 5) {
        timerElement.classList.add("time-warning");
    } else if (tempo <= 5) {
        timerElement.classList.add("time-danger");
    }

    // Quando chega a zero
    if (tempo <= 0) {
        clearInterval(countdown);
        timerElement.textContent = "⏰ Tempo esgotado!";
        progressBar.classList.remove("bg-danger");
        progressBar.classList.add("bg-secondary");
        progressBar.style.width = "0%";
    }
}, 1000);






function mostrarHorario() {
    const agora = new Date();
    let horas = agora.getHours().toString().padStart(2, '0');
    let minutos = agora.getMinutes().toString().padStart(2, '0');
    let segundos = agora.getSeconds().toString().padStart(2, '0');

    document.getElementById("hora").textContent = `${horas}:${minutos}:${segundos}`;
}


mostrarHorario();
setInterval(mostrarHorario, 1000);






function iniciarContagem(dataInicio, tempoTotalSegundos) {
    let timerElement = document.getElementById('timer');
    let progressBar = document.getElementById('progress-bar');

    let inicioMs = new Date(dataInicio).getTime(); // Converte para timestamp
    let fimMs = inicioMs + (tempoTotalSegundos * 1000);

    let countdown = setInterval(() => {
        let agora = new Date().getTime();
        let restanteMs = fimMs - agora;

        // Converte para segundos
        let restante = Math.max(0, Math.floor(restanteMs / 1000));
        timerElement.textContent = restante;

        // Atualiza barra de progresso
        let percent = (restante / tempoTotalSegundos) * 100;
        progressBar.style.width = percent + "%";

        // Efeitos visuais
        timerElement.classList.remove("time-warning", "time-danger");
        if (restante <= 10 && restante > 5) {
            timerElement.classList.add("time-warning");
        } else if (restante <= 5) {
            timerElement.classList.add("time-danger");
        }

        // Quando chega a zero
        if (restante <= 0) {
            clearInterval(countdown);
            timerElement.textContent = "⏰ Tempo esgotado!";
            progressBar.classList.remove("bg-danger");
            progressBar.classList.add("bg-secondary");
            progressBar.style.width = "0%";
        }
    }, 1000);
}


