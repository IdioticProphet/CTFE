function add_elements(category){
	var element_array, i;
	element_array = document.getElementsByClassName("filterItem");
	for (let ele of element_array) {
		if (ele.className.indexOf(category) > 1) ele.classList.add("show");
	}
    nothing_here();
}

function remove_elements(category){
	var element_array, i;
	element_array = document.getElementsByClassName("filterItem");
	for(let ele of element_array) {
		if (ele.className.indexOf(category) > -1) ele.classList.remove("show");
	}
    nothing_here();
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

function nothing_here() {
    var b = false;
    var element_array = document.getElementsByClassName("filterItem");
    for(let ele of element_array) {
        if (ele.className.indexOf("show") > -1) b=true;
    }
    if (b) {
        // do nothing
        document.getElementById("nothing_to_see_here").classList.add("hidden");
        document.getElementById("nothing_to_see_here").classList.remove("not-hidden");
    } else {
        // nothing to see here
        document.getElementById("nothing_to_see_here").classList.remove("hidden");
        document.getElementById("nothing_to_see_here").classList.add("not-hidden");
    }
}