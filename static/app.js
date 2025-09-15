
let tempo = parseInt("{{ tempo }}"); // Recebe do Flask
let timerElement = document.getElementById('timer');
let progressBar = document.getElementById('progress-bar');

let tempoInicial = tempo;














function iniciarContagem(dataInicio, tempoTotalSegundos) {
    tempoTotalSegundos = parseInt(tempoTotalSegundos); 
    let timerElement = document.getElementById('timer');
    let progressBar = document.getElementById('progress-bar');

    let inicioMs = new Date(dataInicio).getTime(); // Converte para timestamp
    let fimMs = inicioMs + (tempoTotalSegundos * 1000);

   
}


