const dropZone = document.getElementById("drop_zone");
const overlay = document.getElementById("overlay");
const pdfObject = document.getElementById("pdf_object");
let dragCounter = 0;
const pdf = document.querySelector(".pdf");
const conBox = document.querySelector(".con_box");

// Include marked.js for Markdown parsing
const script = document.createElement("script");
script.src =
  "https://cdnjs.cloudflare.com/ajax/libs/marked/4.3.0/marked.min.js";
document.head.appendChild(script);

// Prevent default drag behaviors
["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
  document.addEventListener(eventName, (e) => {
    e.preventDefault();
    e.stopPropagation();
  });
});

// Show drop zone when a file is dragged in
document.addEventListener("dragenter", (e) => {
  if (e.dataTransfer?.types?.includes("Files")) {
    dragCounter++;
    dropZone.style.display = "block";
    overlay.style.display = "block";
    conBox.style.filter = "blur(5px)";
  }
});

// Hide drop zone when file leaves
document.addEventListener("dragleave", (e) => {
  dragCounter--;
  if (dragCounter === 0) {
    dropZone.style.display = "none";
    overlay.style.display = "none";
    conBox.style.filter = "blur(0px)";
  }
});

// Handle file drop
document.addEventListener("drop", (e) => {
  dropZone.style.display = "none";
  overlay.style.display = "none";
  dragCounter = 0;
  conBox.style.filter = "blur(0px)";
  pdf.classList.toggle("active");

  const files = e.dataTransfer.files;
  if (files.length > 0) {
    const file = files[0];
    if (file.type === "application/pdf") {
      pdfObject.data = URL.createObjectURL(file);
    } else {
      alert("Please drop a valid PDF file.");
    }
  }
});

// chat box empty handler
document.addEventListener("DOMContentLoaded", function () {
  const userInput = document.getElementById("userInput");

  userInput.addEventListener("input", function () {
    if (userInput.innerHTML === "<br>") {
      userInput.innerHTML = "";
    }

    // Toggle class when input is empty or not
    this.classList.toggle("not-empty", this.innerText.trim().length > 0);
  });

  userInput.addEventListener("focus", function () {
    if (userInput.innerHTML === "<br>") {
      userInput.innerHTML = "";
    }
  });

  userInput.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
      event.preventDefault(); // Prevent new line

      if (this.innerText.trim().length > 0) {
        sendMessage();
        document.querySelector(".hello").style.display = "none";
        this.innerHTML = "";
        this.classList.remove("not-empty");
      }
    }
  });
});

// send click event
const arrow = document.querySelector(".arrow");
arrow.addEventListener("click", function () {
  document.querySelector(".hello").style.display = "none";
});

// data_tab
document.addEventListener("DOMContentLoaded", function () {
  const dbText = document.querySelector(".Database_text");
  const dbBar = document.querySelector(".database_bar");

  dbText.addEventListener("click", function (event) {
    dbBar.style.display = "block";
    event.stopPropagation(); // Prevents triggering the document click event
  });

  document.addEventListener("click", function (event) {
    if (!dbBar.contains(event.target) && !dbText.contains(event.target)) {
      dbBar.style.display = "none";
    }
  });
});
// dataset
let use_dataset_bu = true; // Declare with 'let' to maintain scope

document.getElementById("use_dataset").addEventListener("click", function () {
  document.getElementById("use_dataset").classList.toggle("active");
  use_dataset_bu = false; // This will now update correctly
});

// Send message function with Markdown rendering
async function sendMessage() {
  let userInput = document.getElementById("userInput").innerText.trim();
  let chatbox = document.getElementById("chatbox");

  if (!userInput) return;

  chatbox.innerHTML += `<div class="rep"> <h2>User</h2> ${userInput} </div>`;
  document.getElementById("userInput").innerText = "";

  try {
    let response = await fetch("http://127.0.0.1:5000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: userInput,
        modle_name: "gemma2:2b",
        use_dataset: use_dataset_bu,
      }),
    });

    if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

    let data = await response.json();
    let formattedResponse = marked.parse(data.response); // Convert Markdown to HTML

    chatbox.innerHTML += `<div class="rep"> <h2 class="friday">Friday</h2> ${formattedResponse} </div>`;
    chatbox.scrollTop = chatbox.scrollHeight;
  } catch (error) {
    console.error("Error:", error);
    chatbox.innerHTML += `<div class="rep"> <h2>Friday</h2> Error connecting to server. </div>`;
  }
}

// surch funtion
let fileData = [];
let filteredData = [];
let currentPage = 1;
const recordsPerPage = 10;

// Load JSON file dynamically
fetch("file_metadata.json")
  .then((response) => response.json())
  .then((data) => {
    fileData = data;
    filteredData = data;
    loadTable();
  })
  .catch((error) => console.error("Error loading JSON:", error));

function loadTable() {
  const tableBody = document.getElementById("tableBody");
  tableBody.innerHTML = "";

  let startIndex = (currentPage - 1) * recordsPerPage;
  let endIndex = startIndex + recordsPerPage;
  let paginatedData = filteredData.slice(startIndex, endIndex);

  function formatDate(dateString) {
    const date = new Date(dateString);

    const day = date.getDate();
    const month = date.toLocaleString("en-US", { month: "short" });
    const year = date.getFullYear().toString().slice(-2);

    return `${day} ${month} ${year}`;
  }

  paginatedData.forEach((file) => {
    let row = document.createElement("tr");
    row.classList.add("table-row");

    // row.innerHTML = `
    //               <td class="table-cell">${file.file}</td>
    //               <td class="table-cell">${file.file_type}</td>
    //               <td class="table-cell">${file.created_date}</td>
    //             `;

    row.innerHTML = `
                  <td class="table-cell"><input type="checkbox" id="checked" checked>${
                    file.file
                  }</td>
                  <td class="table-cell">${formatDate(file.created_date)}</td>
                `;
    tableBody.appendChild(row);
  });

  updatePagination();
}

function searchTable() {
  let query = document.getElementById("searchInput").value.toLowerCase();
  filteredData = fileData.filter(
    (file) =>
      file.file.toLowerCase().includes(query) ||
      file.file_type.toLowerCase().includes(query) ||
      file.created_date.toLowerCase().includes(query)
  );

  currentPage = 1;
  loadTable();
}

function changePage(direction) {
  currentPage += direction;
  loadTable();
}

function updatePagination() {
  document.getElementById(
    "pageInfo"
  ).innerText = `Page ${currentPage} of ${Math.ceil(
    filteredData.length / recordsPerPage
  )}`;

  // Enable/Disable buttons based on page count
  document
    .getElementById("prevBtn")
    .classList.toggle("disabled", currentPage === 1);
  document
    .getElementById("nextBtn")
    .classList.toggle(
      "disabled",
      currentPage * recordsPerPage >= filteredData.length
    );
}
