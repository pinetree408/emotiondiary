var playing = false; 
       
var effBoxWidth = 360;  // = 480 -120 (actual - word size)
var effBoxHt = 340; // = 380 - 40 (actual - word height)
    
// 0 = red; 1 = green; 2 = blue; 3 = yellow:
var curColor;
var numShown;
var numTried;
var numCorrect;

var correctItemFactor = 1;
var allCorrectBonus = 0; 
var totalPossibleScore;

var flashOnTimer = true;
var flashMode = 1;  //0 = off; 1 = on
var flashTime;
var flashOnTimeLimit = 1;  //clockticks
var flashOffTimeLimit = 1; //clockticks
var timeoutamt=1;
  
function initialStartGame() {
  setCurrentSpeed();
  startGame();
}


function startGame()
{
  reset_timer();
  initialize();
  flashOn();
  start_timer();

  var containerdiv = document.getElementById('stroop_container');
  var slocatediv = document.getElementById('stroop-locate');
  var bboxdiv = document.getElementById('buttons-container');

  var slocateem = slocatediv.clientHeight/9.0;
  effBoxWidth = slocatediv.clientWidth - 2 * bboxdiv.clientWidth;
  effBoxHt = containerdiv.clientHeight - 1.1 * slocateem;

  nextDisplay();
}

function initialize()
{
  curColor = 0;
  numShown = 0;
  numTried = 0;
  numCorrect = 0;

  setNumTried();
  setCorrect();
}

function stopGame()
{
  stop_timer();
  hideWord();
}

// random integer 0 <= X < n:
function rnd(n) {
  return Math.floor(Math.random() * n);
}

function rndColor() {
  var nn = rnd(4);
  var slocatediv = document.getElementById('stroop-locate');

  // 0 = red; 1 = green; 2 = blue; 3 = yellow:
  curColor = nn;
  if (nn == 0){
     slocatediv.style.color = '#FF0000';   // red
  } else if (nn == 1) {
     slocatediv.style.color = '#00FF00';   // green
  } else if (nn == 2) {
     slocatediv.style.color = '#0000FF';   // blue
  } else if (nn == 3) {
     slocatediv.style.color = '#FFD700';   // golden yellow
  }
}

function doNextDisplay()
{
  nextDisplay();
}

function nextDisplay() {
  increaseNumShown();

  var slocatediv = document.getElementById('stroop-locate');
  slocatediv.style.marginLeft = rnd(effBoxWidth) + 'px';
  slocatediv.style.marginTop = rnd(effBoxHt) + 'px';

  rndColor();
  rndWord();
}

function rndWord()
{
  var slocatediv = document.getElementById('stroop-locate');
  var nn = rnd(4);
  while (nn == curColor){
      nn = rnd(4);
  }
  if (nn == 0){
     slocatediv.innerHTML = '빨강';
  } else if (nn == 1) {
     slocatediv.innerHTML = '초록';
  } else if (nn == 2) {
     slocatediv.innerHTML = '파랑';
  } else if (nn == 3) {
     slocatediv.innerHTML = '노랑';
  }
}

function hideWord() {
  var slocatediv = document.getElementById('stroop-locate');
  slocatediv.innerHTML = '';
}

function respond(response)
{
  var respNum = parseInt(response);
  incrNumTried();
  if (respNum == curColor){
    numCorrect++;
    setCorrect();
  }
  flashOn();
  nextDisplay();
}

function increaseNumShown() {
  numShown++;
  setNumShown();
}

function setNumShown()
{
  var numshown_div = document.getElementById('numshown_div');
  numshown_div.innerHTML = numShown;
}

function incrNumTried()
{
  numTried++;
  setNumTried();
}

function setNumTried() {
  var numtried_div = document.getElementById('numtried_div');
  numtried_div.innerHTML = numTried;
}

function setCorrect() {
  var numcorrectdiv = document.getElementById('numcorrect_div');
  numcorrectdiv.innerHTML = numCorrect;
}

//--------Elapsed time code -------------

function doFlash() {
  if (flashTime == 0) {
    flashMode = 1 - flashMode;
    if (flashMode == 0){
       hideWord();
       flashTime = flashOffTimeLimit;
    } else {
       nextDisplay();
       flashTime = flashOnTimeLimit;
    }
  } else {
    flashTime--;
  }
}

function  flashOn() {
  flashMode = 1;
  flashTime = flashOnTimeLimit;
}

function reset_timer()
{
  start_time = null;
  var timediv = document.getElementById('elaps_time_div');
  timediv.innerHTML = "00:00";
}

function changeSpeed()
{
  setCurrentSpeed();
}

function setCurrentSpeed() {
  var speedselect = document.getElementById('taskspeed');
  taskspeed = speedselect.value;
  if (taskspeed=='Slow'){
    timeoutamt=600;
  } else if (taskspeed=='Medium'){
    timeoutamt=500;
  } else if (taskspeed=='Fast'){
    timeoutamt=400;
  } else {
    timeoutamt=300;
  }
}

/* =========== Elapsed time code ===========  */

var timeout_id = 0;
var start_time  = 0;
var elapsed_time = 0;
var elapsed_mins = 0;
var elapsed_secs = 0;
var total_offset_secs = 0;

function update_timer() {
  if (timeout_id) {
    clearTimeout(timeout_id);
  }

  if (!start_time) {
    start_time = new Date();
  }

  var cur_time = new Date();
  elapsed_time = cur_time.getTime() - start_time.getTime() + total_offset_secs * 1000;

  cur_time.setTime(elapsed_time);
  elapsed_mins = cur_time.getMinutes();
  elapsed_secs = cur_time.getSeconds();
  var selapsed_secs = elapsed_secs;
  if (elapsed_secs < 10){
      selapsed_secs = "0" + elapsed_secs;
  }

  var timediv = document.getElementById('elaps_time_div');
  timediv.innerHTML =  "" + elapsed_mins + ":" + selapsed_secs;

  if (flashOnTimer) {
    doFlash();
  }

  timeout_id = setTimeout(update_timer, timeoutamt);
}

function start_timer() {
  if (!start_time) {
    start_time = new Date();
    var timediv = document.getElementById('elaps_time_div');
    timediv.innerHTML = "00:00";
    timeout_id = setTimeout(update_timer, 1000);
  }
}


function restart_timer(secs) {
  total_offset_secs = secs;

  start_mins = Math.floor(secs/60);
  start_secs = secs % 60;
  var sstart_secs = start_secs;
  if (start_secs < 10){
    sstart_secs = "0" + start_secs;
  }
  var theTime = start_mins.toString()+ ":" + sstart_secs;

  var timediv = document.getElementById('elaps_time_div');
  timediv.innerHTML = theTime;

  stop_timer();
  start_time   = new Date();
  timeout_id  = setTimeout(update_timer, 1000);
}

function stop_timer() {
  if(timeout_id) {
    clearTimeout(timeout_id);
    timeout_id  = 0;
  }
  start_time = null;
}

function reset_timer() {
  start_time = null;

  var timediv = document.getElementById('elaps_time_div');
  timediv.innerHTML = "00:00";
}

function showInstructions() {
  var ipath= "http://webst-kaist.org/maps/stroop_mnl.html";
  var entry_win=window.open(ipath,'Stroop_Task_Instructions','height=400,width=650');
  return false;
}
