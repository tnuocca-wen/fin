function generate(ticker, year, qrtr, ser) {
  genbtn = document.getElementById("gen_btn");
  if (genbtn) {
    genbtn.addEventListener("click", (e) => {
      e.preventDefault();
      // circLoader();
      formdata = new FormData();
      console.log(ticker, year, qrtr);
      formdata.append("link", genbtn.href);
      formdata.append("ticker", ticker);
      formdata.append("year", year);
      formdata.append("quarter", qrtr);
      formdata.append("service", ser);
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
          pdfbtn_create(doc_root+"/"+ticker+"/"+year+"/"+qrtr+"/"+ticker+".pdf");
          fin_parent.innerHTML = ``;
          const fin_text = document.createElement("div");
          fin_text.id = "fin_text";
          fin_text.style.overflowY = "auto";
          fin_text.style.height = "97vh";
          fin_text.style.border = "1px dashed gray;";
          fin_text.style.whiteSpace = "pre-line";
          document.getElementById("fin_parent").appendChild(fin_text);
          // Function to consume the streaming data
          const processStream = ({ value, done }) => {
            if (done) {
              console.log("Streaming response complete.", done);
              if (response.status != 205){
                fin_text.innerHTML += value;
              upl_data(done, ticker, year, qrtr, ser);}
              return;
            }
            // Assuming the streaming response is text data
            const chunk = new TextDecoder().decode(value);
            // chunk.replace("\n", "<br>");
            console.log(chunk);
            fin_text.innerHTML += chunk;
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

function upl_data(done, ticker, year, qrtr, ser){
  // console.log(JSON.stringify({"done": done, "tic": ticker, "yr": year, "qr": qrtr}));
  data = new FormData();
  data.append("dat", JSON.stringify({"done": done, "tic": ticker, "yr": year, "qr": qrtr, "sr": ser}))
  fetch(upl_url, {
    method: 'POST',
    body: data,
    headers: {
      "X-CSRFToken": csrf_token,
    },
  }).then(response => {
    console.log(response);
    if (ser != 1){
      strtktelab();
    }
  })
}

function strtktelab(){

}
