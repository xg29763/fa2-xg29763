function articleSearch() {
  // Declare variables 
  var input, filter, table, tr, td, i, j, txtValue;
  input = document.getElementById("articleSearch");
  filter = input.value.toUpperCase();
  table = document.getElementById("articleTable");
  tr = table.getElementsByTagName("tr");

  // Loop through all table rows, and hide those who don't match the search query
  for (i = 0; i < tr.length; i++) {
    loop1:
    for (j = 0; j < 8; j++) {
      td = tr[i].getElementsByTagName("td")[j];
      if (td) {
        txtValue = td.textContent || td.innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
          tr[i].style.display = "";
          break loop1;
        } else {
          tr[i].style.display = "none";
        }
      }
    }
  }
}