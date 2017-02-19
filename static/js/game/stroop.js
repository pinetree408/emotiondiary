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
//var clocktick = 100;       //millisecs
var timeoutamt=1;
  
//var primaryParent;
//var statisticsdiv;
var containerdiv;
var slocatediv;

function onPageLoaded()
{ 
//  statisticsdiv = document.getElementById('tried_correct_statistics');
//  primaryParent = statisticsdiv.parentNode;
//  statisticsdiv = primaryParent.removeChild(statisticsdiv);
}
  

function initialStartGame()
{
//  var textdiv = document.getElementById('intro_text');
//  primaryParent.insertBefore(statisticsdiv, textdiv);
//  textdiv.innerHTML='';
//  setupStartStop();

  setCurrentSpeed();

  containerdiv = document.getElementById('stroop_container');
    
  var msgsdiv = document.createElement('div');
  msgsdiv.id = 'user_messages';
//  primaryParent.insertBefore(msgsdiv, containerdiv);

  startGame();
}


function startGame()
{
    reset_timer();
    initialize();
    flashOn();
    start_timer();
//    setStopStartBtns(false, true);

//    var statisticsdiv = document.getElementById('tried_correct_statistics');
//        statisticsdiv.style.display='block';

    containerdiv = document.getElementById('stroop_container');
    slocatediv = document.getElementById('stroop-locate');
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
//    setStopStartBtns(true, false);
   // totalPossibleScore= numTried  * correctItemFactor + allCorrectBonus;
 //   var userNum = sbCookieData.usernum;
  //      Record.recordNumCorrectPlusMovesWithMax(taskId, numTried, numCorrect, elapsed_time, totalPossibleScore, userNum);
}

  // random integer 0 <= X < n:
function rnd(n) {
  return Math.floor(Math.random() * n);
}

function rndColor()
{
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

function nextDisplay()
{
    incrNumShown();
    rndColor();
    containerdiv.removeChild(slocatediv);
    slocatediv.style.marginLeft = rnd(effBoxWidth) + 'px';
    slocatediv.style.marginTop = rnd(effBoxHt) + 'px';
    console.log(slocatediv);
    rndWord();
    containerdiv.appendChild(slocatediv);
}

function rndWord()
{
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

function hideWord()
{
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

function incrNumShown()
{
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
function setNumTried()
{
  var numtried_div = document.getElementById('numtried_div');
  numtried_div.innerHTML = numTried;
}
function setCorrect()
{
  var numcorrectdiv = document.getElementById('numcorrect_div');
  numcorrectdiv.innerHTML = numCorrect;
}

        //--------Elapsed time code -------------

function doFlash()
{
   if (flashTime == 0)
   {
      var lastFlashMode = flashMode;
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

function  flashOn()
{
  flashMode = 1;
  flashTime = flashOnTimeLimit;
}

function reset_timer()
{
   start_time = null;
/*
      if (time_display_type == 1){
           document.topform.timeDisplay.value = "00:00";
      } else {
*/
           var timediv = document.getElementById('elaps_time_div');
           timediv.innerHTML = "00:00";
//      }
}

function changeSpeed()
{
    setCurrentSpeed();
}

function setCurrentSpeed()
{
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

var time_display_type = 0;  /* type 0 = div-based; type 1 = form-based (deprecated) */
var timeout_id = 0;
var start_time  = 0;
var elapsed_time = 0;
var elapsed_mins = 0;
var elapsed_secs = 0;
var total_offset_secs = 0;

function update_timer()
{
   if (timeout_id) {
      clearTimeout(timeout_id);
      timeout_id = 0;
   }

   if (!start_time)
       start_time = new Date();

   var cur_time = new Date();
   elapsed_time = cur_time.getTime() - start_time.getTime() + total_offset_secs * 1000;

   cur_time.setTime(elapsed_time);
   elapsed_mins = cur_time.getMinutes();
   elapsed_secs = cur_time.getSeconds();
   var selapsed_secs = elapsed_secs;
   if (elapsed_secs < 10){
       selapsed_secs = "0" + elapsed_secs;
   }

   if (time_display_type == 1){
        document.topform.timeDisplay.value = "" + elapsed_mins + ":" + selapsed_secs;
   } else {
        var timediv = document.getElementById('elaps_time_div');
        timediv.innerHTML =  "" + elapsed_mins + ":" + selapsed_secs;
   }

   if (flashOnTimer)
   {
         // to be implemented by pages which set flashOnTimer = true:
      doFlash();
   }


//   timeout_id = setTimeout("update_timer()", 1000);
   timeout_id = setTimeout("update_timer()", timeoutamt);
}

//var flashOnTimer = false;
function start_timer()
{
   if (!start_time)
   {
      start_time   = new Date();
      if (time_display_type == 1){
           document.topform.timeDisplay.value = "00:00";
      } else {
           var timediv = document.getElementById('elaps_time_div');
           timediv.innerHTML = "00:00";
      }
      timeout_id  = setTimeout("update_timer()", 1000);
   }
}


function restart_timer(secs)
{
    total_offset_secs = secs;

    start_mins = Math.floor(secs/60);
    start_secs = secs % 60;
    var sstart_secs = start_secs;
    if (start_secs < 10){
       sstart_secs = "0" + start_secs;
    }
    var theTime = start_mins.toString()+ ":" + sstart_secs;

      if (time_display_type == 1){
           document.topform.timeDisplay.value = theTime;
      } else {
           var timediv = document.getElementById('elaps_time_div');
           timediv.innerHTML = theTime;
      }
    stop_timer();
    start_time   = new Date();
    timeout_id  = setTimeout("update_timer()", 1000);
}


function stop_timer()
{
   if(timeout_id) {
      clearTimeout(timeout_id);
      timeout_id  = 0;
   }
   start_time = null;
}

function reset_timer()
{
   start_time = null;
      if (time_display_type == 1){
           document.topform.timeDisplay.value = "00:00";
      } else {
           var timediv = document.getElementById('elaps_time_div');
           timediv.innerHTML = "00:00";
      }
}


function showInstructions()
{
    var ipath= "http://webst-kaist.org/maps/stroop_mnl.html";
    var entry_win=window.open(
                     ipath,
                     'Stroop_Task_Instructions',
                     'height=400,width=650');
    return false;
}
