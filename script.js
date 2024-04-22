let mouse = false;
let framesInShot = 0;
let animating = false;
let gameEnd = false;

let turn = "p1";
$(document).ready(function() {
    addEventListeners();

    document.addEventListener("click", function(event) {
        addEventListeners();
        mouse = false;
        letGo(event);
    });

    document.addEventListener("mousemove", function(event) {
        if (mouse) {
            console.log("WE MOVIN");
            mouseMove(event);
        }
    });

    let p = document.createElement("p");
    p.id = "currentTurn";
    document.getElementById("p1").appendChild(p);
    p.innerHTML = "Current Turn";

    addEventListeners();
});

function addEventListeners() {
    let cueDef = document.getElementById("cue");


    if (cueDef) {
        cueDef.addEventListener("mousedown", function(event) {
            mouseDown(event);
            mouse = true;
        });
    }
}

function mouseMove(event) {
    if (!animating && !gameEnd) {
        let line = document.getElementById("line");
        let svg = document.getElementsByTagName("svg")[0];
        let cue = svg.getElementById("cue");
        if (!line) {
            line = document.createElementNS("http://www.w3.org/2000/svg", "line");
            line.setAttribute("id", "line");
            line.setAttribute("stroke-width", "25");
            line.setAttribute("stroke", "black");
            svg.appendChild(line);
        }

        line.setAttribute("x1", 2 * (event.pageX - svg.getBoundingClientRect().left) - 25);
        line.setAttribute("y1", 2 * (event.clientY - svg.getBoundingClientRect().top) - 25);
        line.setAttribute("x2", cue.cx.baseVal.value);
        line.setAttribute("y2", cue.cy.baseVal.value);
    }
}

function mouseDown(event) {
}

let theInterval;
let tableId = 1;
let originalSVG;
let lastSVG;
let done = 0;
function letGo(event) {
    if (!animating && !gameEnd) {
        animating = true;
        done = 0;
        tableId = 1;
        console.log("MOUSEUP");
        let svg = document.getElementsByTagName("svg")[0];

        if (!svg) {
            return;
        }

        let line = svg.getElementById("line");

        if (!line) {
            return; 
        }

        let x1 = line.x1.baseVal.value;
        let x2 = line.x2.baseVal.value;
        let y1 = line.y1.baseVal.value;
        let y2 = line.y2.baseVal.value;
        let x = 2.5 * (x2 - x1);
        let y = 2.5 * (y2 - y1);

        console.log("X: " + x + ", Y: " + y);

        if (Math.sqrt(x * x + y * y) > 10000) {
            let ratio = x / y;
            let ratio2 = y / x;
            while (Math.sqrt(x * x + y * y) > 10000) {
                x -= ratio;
                y -= ratio2;
            }
        }

        console.log(line);
        if (line) {
            line.remove();
        }

        originalSVG = svg;

        console.log(event);

        //Send to server
        let xhr = new XMLHttpRequest();
        let url = "http://localhost:57643/amongus.html";

        let myArray = [x, y];
        let jsonString = JSON.stringify(myArray);

        setTimeout(function() {
            theInterval = setInterval(fetchDataFromServer, 100);
        }, 10000);

        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    console.log("Frames in Shot: " + xhr.responseText);
                    framesInShot = parseInt(xhr.responseText);
                } else {
                    console.error('Request failed with status:', xhr.status);
                }
            }
        };

        xhr.open("POST", url, true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.send(jsonString);
    }
}

function fetchDataFromServer() {
    request = $.get("table" + tableId + ".svg", function(data) {
        string = (new XMLSerializer()).serializeToString(data);
        $("svg").remove();
        $("#middleTable").append(string);
        lastSVG = document.getElementsByTagName("svg")[0];
        addEventListeners();
    });

    request.fail(leaveXML);

    if (tableId == framesInShot) {
        leaveXML();
        animating = false;
        clearInterval(theInterval);

        addEventListeners();
    }
    tableId++;
}

function leaveXML() {
    if (done == 0) {
        animating = false;
        done = 1;
        tableId = 1;
        console.log("FAILLL");
        clearInterval(theInterval);

        afterShot();

        addEventListeners();
    }
}

function printSVGs() {
    console.log(originalSVG);
    console.log(lastSVG);

    return [originalSVG, lastSVG];
}

function parseSVG(svg) {
    let x = {
        p1: 0,
        p2: 0,
        has8: false,
        hasCue: false
    }
    for (let i = 11; i < 27; i++) {
        if (!svg.children[i]) {
            continue;
        }
        let fill = svg.children[i].getAttribute("fill");

        if (fill == "YELLOW" || fill == "BLUE" || fill == "RED" || fill == "PURPLE" || fill == "ORANGE" || fill == "GREEN" || fill == "BROWN") {
            x.p1++;
        }
        else if (fill != "BLACK" && fill != "WHITE") {
            x.p2++;
        }
        else if (fill == "BLACK") {
            x.has8 = true;
        }
        else if (fill == "WHITE") {
            x.hasCue = true;
        }
    }

    console.log(x);
    return x;
}

let hasSankFirst = false;
function afterShot() {
    console.log("AFTER SHOT");
    let pre = parseSVG(originalSVG);
    let post = parseSVG(lastSVG);

    let p1Diff = pre.p1 - post.p1;
    let p2Diff = pre.p2 - post.p2;

    if (turn == "p1") {
        if (p1Diff > 0) {
            turn = "p1";
        }
        else {
            turn = "p2";
        }

        if (!post.has8) {
            if (post.p1 == 0) {
                console.log("PLAYER 1 WINS");
                win(1);
            }
            else {
                console.log("PLAYER 2 WINS");
                win(2);
            }
        }
    }
    else {
        if (p2Diff > 0) {
            turn = "p2";
        }
        else {
            turn = "p1";
        }

        if (!post.has8) {
            if (post.p2 == 0) {
                console.log("PLAYER 1 WINS");
                win(1);
            }
            else {
                console.log("PLAYER 2 WINS");
                win(2);
            }
        }
    }

    console.log(turn);

    let div = document.getElementById("currentTurn");
    if (div != null) {
        div.remove();
    }
    if (turn == "p1") {
        let p = document.createElement("p");
        p.id = "currentTurn";
        document.getElementById("p1").appendChild(p);
        p.innerHTML = "Current Turn";
    }
    else {
        let p = document.createElement("p");
        p.id = "currentTurn";
        document.getElementById("p2").appendChild(p);
        p.innerHTML = "Current Turn";
    }
}

function win(num) {
    gameEnd = true;
    document.getElementById("currentTurn").remove();
    let p = document.createElement("p");
    p.classList.add("gameOver");
    document.getElementById("p1").appendChild(p);
    document.getElementById("p2").appendChild(p);
    if (num == 1) {
        p.innerHTML = `
        Game Over.
        Player 1 Wins.
        `
    }
    else {
        p.innerHTML = `
        Game Over.
        Player 2 Wins.
        `
    }
}