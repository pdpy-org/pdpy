const Envelop = (target, {
  node = target,
  param = 'gain',
  attack = 50,
  release = 500,
  start = 0,
  end = 1,
  duration = attack + release,
  time = context.currentTime,
  endTime = time + duration * 0.001,
  doneAction = 0
}={}) => new Promise ( resolve => {

  node[param].cancelScheduledValues(time);
  node[param].setValueAtTime(start, time);
  node[param].linearRampToValueAtTime(end, time + attack * 0.001);
  node[param].linearRampToValueAtTime(start, endTime);

  if (doneAction !== 0) {
    target.start(time);
    console.log(duration);
    new Promise(resolve => setTimeout(resolve, duration))
      .then( () => doneAction(target, endTime))
      .then( () => resolve() );
  }
  
});