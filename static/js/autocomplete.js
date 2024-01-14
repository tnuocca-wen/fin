/*
    autocomplete company names
    */
let controller = null;
function get_arr(val) {
  if (controller) {
    controller.abort();
    controller = null;
  }

  controller = new AbortController();

  formdata = new FormData();
  formdata.append("nameval", val);
  return fetch(auto_url, {
    method: "POST",
    body: formdata,
    signal: controller.signal,
    headers: {
      "X-CSRFToken": csrf_token
  }
  })
    .then((response) => response.json())
    .then((data) => {
      return data.cdict;
    })
    .catch((error) => {
      //   console.log("");
    });
  // .finally(() => {
  //   controller = null;
  // })
}
// let arr = null;
// get_arr("tat").then(result =>{
//   arr = result;
//   console.log(arr);
// });

function autocomplete(inp, year, quar) {
  /*the function has three arguments the textarea, the select element for the year and the select element for the quarter.*/
  var currentFocus;
  // a = document.getElementById('parent-options');
  /*execute a function when someone writes in the text field:*/
  inp.addEventListener("input", function (e) {
    var b,
      i,
      val = this.value;
    /*close any already open lists of autocompleted values*/
    if (!val) {
      closeAllLists();
      return false;
    }
    currentFocus = -1;
    if (val != "") {
      get_arr(val)
        .then((result) => {
          closeAllLists();
          if (!val) {
            closeAllLists();
            return false;
          }
          arr = result;
          companies = result;
          console.log(arr);
          /*create a DIV element that will contain the items (values):*/
          a = document.createElement("div");
          a.id = "parent-options";
          a.classList.add("parent-options");
          a.style.zIndex = "1000";
          /*append the DIV element as a child of the autocomplete container:*/
          this.parentNode.appendChild(a);
          /*for each item in the array...*/
          try {
            if (val != "") {
              for (i = 0; i < arr.length; i++) {
                /*check if the item starts with the same letters as the t ext field value:*/
                // if (arr[i][0].substr(0, val.length).toUpperCase() == val.toUpperCase() || arr[i][1].substr(0, val.length).toUpperCase() == val.toUpperCase()) {
                /*create a DIV element for each matching element:*/
                b = document.createElement("div");
                b.classList.add("options");
                /*make the matching letters bold:*/
                // b.innerHTML = "<strong>" + arr[i][0].substr(0, val.length) + "</strong>";
                // b.innerHTML += arr[i][0].substr(val.length);
                b.innerHTML = arr[i][0];
                b.innerHTML += " (" + arr[i][1] + ")";
                /*insert a input field that will hold the current array item's value:*/
                b.innerHTML +=
                  "<input type='hidden' value='" + arr[i][0] + "'>";
                /*execute a function when someone clicks on the item value (DIV element):*/
                b.addEventListener("click", function (e) {
                  /*insert the value for the autocomplete text field:*/
                  inp.value = this.getElementsByTagName("input")[0].value;
                  for (j = 0; j < arr.length; j++) {
                    if (
                      this.getElementsByTagName("input")[0].value == arr[j][0]
                    ) {
                      tarr = [];
                      tarr.push(arr[j][2]);
                      for (l = 0; l < arr[j][4].length; l++) {
                        tarr.push(arr[j][4][l]);
                      }
                      console.log(tarr);
                      tarr.sort(function (a, b) {
                        return b - a;
                      });
                      while (year.firstChild) {
                        year.removeChild(year.firstChild);
                      }
                      for (k = 0; k < tarr.length; k++) {
                        if (tarr[k - 1] != tarr[k]) {
                          var option = document.createElement("option");
                          option.text = tarr[k]; // Set text for each option
                          option.value = tarr[k];
                          year.appendChild(option);
                        }
                      }
                      while (quar.firstChild) {
                        quar.removeChild(quar.firstChild);
                      }
                      var loption = document.createElement("option");

                      if (arr[j][3] == 1) {
                        loption.text = "One (Q1)"; // Set text for each option
                        loption.value = arr[j][3];
                      } else if (arr[j][3] == 2) {
                        loption.text = "Two (Q2)"; // Set text for each option
                        loption.value = arr[j][3];
                      } else if (arr[j][3] == 3) {
                        loption.text = "Three (Q3)"; // Set text for each option
                        loption.value = arr[j][3];
                      } else if (arr[j][3] == 4) {
                        loption.text = "Four (Q4)"; // Set text for each option
                        loption.value = arr[j][3];
                      }
                      quar.appendChild(loption);

                      qn = [1, 2, 3, 4];
                      for (m = 0; m < qn.length; m++) {
                        if (arr[j][3] == qn[m]) {
                          qn.splice(m, 1);
                          i--;
                        }
                      }
                      for (m = 0; m < qn.length; m++) {
                        var option = document.createElement("option");
                        if (qn[m] == 1) {
                          option.text = "One (Q1)"; // Set text for each option
                          option.value = qn[m];
                        } else if (qn[m] == 2) {
                          option.text = "Two (Q2)"; // Set text for each option
                          option.value = qn[m];
                        } else if (qn[m] == 3) {
                          option.text = "Three (Q3)"; // Set text for each option
                          option.value = qn[m];
                        } else if (qn[m] == 4) {
                          option.text = "Four (Q4)"; // Set text for each option
                          option.value = qn[m];
                        }
                        quar.appendChild(option);
                      }
                    }
                  }
                  // var opt =
                  // year
                  // console.log(inp.value);
                  /*close the list of autocompleted values,
              (or any other open lists of autocompleted values:*/
                  closeAllLists();
                  document.getElementById("submit-btn").click();
                });
                a.appendChild(b);
                // }
              }
            }
          } catch {
            // console.log('ignored');
          }
        })
        .then(() => {
          const keydown = new KeyboardEvent("keydown", {
            keyCode: 40,
          });
          inp.dispatchEvent(keydown);
        });
    }
  });
  /*execute a function presses a key on the keyboard:*/
  inp.addEventListener("keydown", function (e) {
    var y = document.getElementById("parent-options");
    if (y) x = y.getElementsByTagName("div");
    if (e.keyCode == 40) {
      e.preventDefault();
      /*If the arrow DOWN key is pressed,
          increase the currentFocus variable:*/
      //   console.log(currentFocus);
      currentFocus++;
      /*and and make the current item more visible:*/
      addActive(x);
      //   console.log(x[currentFocus].offsetTop);
      //   console.log(y.offsetTop);
      try {
        y.scrollTop = x[currentFocus].offsetTop - y.offsetTop;
      } catch {}
    } else if (e.keyCode == 38) {
      //up
      e.preventDefault();
      /*If the arrow UP key is pressed,
          decrease the currentFocus variable:*/
      currentFocus--;
      /*and and make the current item more visible:*/
      addActive(x);
      y.scrollTop = x[currentFocus].offsetTop - y.offsetTop;
    } else if (e.keyCode == 13) {
      /*If the ENTER key is pressed, prevent the form from being submitted,*/
      e.preventDefault();
      if (currentFocus > -1) {
        /*and simulate a click on the "active" item:*/
        if (x) x[currentFocus].click();
      }
    }
  });

  function addActive(x) {
    /*a function to classify an item as "active":*/
    if (!x) return false;
    /*start by removing the "active" class on all items:*/
    removeActive(x);
    if (currentFocus >= x.length) currentFocus = x.length - 1;
    if (currentFocus < 0) currentFocus = x.length - 1;
    /*add class "autocomplete-active":*/
    try {
      x[currentFocus].classList.add("options-active");
    } catch {
      // console.log('ignored');
    }
  }
  function removeActive(x) {
    /*a function to remove the "active" class from all autocomplete items:*/
    for (var i = 0; i < x.length; i++) {
      x[i].classList.remove("options-active");
    }
  }
  function closeAllLists(elmnt) {
    /*close all autocomplete lists in the document,
      except the one passed as an argument:*/
    var x = document.getElementsByClassName("parent-options");
    for (var i = 0; i < x.length; i++) {
      if (elmnt != x[i] && elmnt != inp) {
        x[i].parentNode.removeChild(x[i]);
      }
    }
  }
  /*execute a function when someone clicks in the document:*/
  document.addEventListener("click", function (e) {
    closeAllLists(e.target);
  });
}

autocomplete(
  document.getElementById("company_field"),
  document.getElementById("YearSelect"),
  document.getElementById("QuarterSelect")
);
