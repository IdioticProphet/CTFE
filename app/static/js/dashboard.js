function add_elements(category){
	var element_array, i;
	element_array = document.getElementsByClassName("filterItem");
	for (let ele of element_array) {
		if (ele.className.indexOf(category) > 1) ele.classList.add("show");
	}
}

function remove_elements(category){
	var element_array, i;
	element_array = document.getElementsByClassName("filterItem");
	for(let ele of element_array) {
		if (ele.className.indexOf(category) > -1) ele.classList.remove("show");
	}
}

function check_box_function(checkboxElement, category) {
	var elem = document.getElementById(`ck${category}`);
	console.log(elem);
	if (elem.checked) {
		add_elements(category);
	} else {
		remove_elements(category);
	}
}