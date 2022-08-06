// import Envelop from '/Envelope'

const play = document.getElementById("play");
const start = document.getElementById("start");
const range = document.getElementById("range");

let context = null, mainGain = null, comp = null;
let initialized = false, started = false;
let retrig = true;

const envTrain = (min,max) => new Promise( resolve => {

  const freq = Math.random() * 100 + 500;
  // const dur = Math.random();

  const osc = context.createOscillator();
  // osc.type = 'sine';
  // osc.frequency.value = freq;

  const oscvol = context.createGain();
  
  const freqParams = {
      release: Math.random() * 20 + 3, 
      param: "frequency", 
      start: freq, 
      end: freq * (Math.random() + 1)
  }
  
  const ampParams = {
    attack: Math.random() * 20 + 3, 
    release: Math.random() * 1000 + 100, 
    node: oscvol, 
    doneAction: (node,time) => node.stop(time)
  }
  
  osc.connect(oscvol).connect(mainGain);

  Envelop(osc, freqParams);

  Envelop(osc, ampParams).then( () => {
    retrig
      ? envTrain(min, max)
      : null;
  } );
  
});

play.onclick = () => {
  if(!initialized) {
    context = new AudioContext();
    play.innerHTML = "Play";
    initialized = true;
    
    mainGain = context.createGain();
    comp = context.createDynamicsCompressor();
    mainGain.gain.setValueAtTime(0, 0);
    
    range.oninput = event => {
      mainGain.gain.linearRampToValueAtTime(event.target.value * 0.01, context.currentTime + 0.1);
    };

    mainGain.connect(comp).connect(context.destination);


  } else {
    envTrain(80, 1000);
  }
}
start.onclick = () => {
  if(!retrig) {
    retrig = true;
    start.innerHTML = "Retrig"
  } else {
    retrig = false;
    start.innerHTML = "Once"
  }
}