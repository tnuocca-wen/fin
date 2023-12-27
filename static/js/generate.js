function generate(ticker, year, qrtr) {
  genbtn = document.getElementById("gen_btn");
  if (genbtn) {
    genbtn.addEventListener("click", (e) => {
      e.preventDefault();
      formdata = new FormData();
      console.log(ticker, year, qrtr);
      formdata.append("link", genbtn.href);
      formdata.append("ticker", ticker);
      formdata.append("year", year);
      formdata.append("quarter", qrtr);
      console.log(formdata);
      fetch(gen_url, {
        method: "POST",
        body: formdata,
        headers: {
          "X-CSRFToken": csrf_token,
        },
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error("Network response was not ok.");
          }
          const reader = response.body.getReader();
          fin_parent.innerHTML = ``;
          const fin_text = document.createElement("div");
          fin_text.id = "fin_text";
          fin_text.style.overflowY = "auto";
          fin_text.style.height = "97vh";
          fin_text.style.border = "1px dashed gray;";
          document.getElementById("fin_parent").appendChild(fin_text);
          // Function to consume the streaming data
          const processStream = ({ value, done }) => {
            if (done) {
              console.log("Streaming response complete.", done);
              upl_data(done, ticker, year, qrtr);
              return;
            }
            // Assuming the streaming response is text data
            const chunk = new TextDecoder().decode(value);
            if (chunk != 'None'){
            fin_text.innerHTML += chunk;}
            // Continue reading the stream
            return reader.read().then(processStream);
          };

          // Start reading the stream
          return reader.read().then(processStream);
        })
        .catch((error) => {
          console.error("There was a problem with the fetch operation:", error);
        });
    });
  }
}

function upl_data(done, ticker, year, qrtr){
  // console.log(JSON.stringify({"done": done, "tic": ticker, "yr": year, "qr": qrtr}));
  data = new FormData();
  data.append("dat", JSON.stringify({"done": done, "tic": ticker, "yr": year, "qr": qrtr}))
  fetch(upl_url, {
    method: 'POST',
    body: data,
    headers: {
      "X-CSRFToken": csrf_token,
    },
  }).then(response => {
    console.log(response);
  })
}
