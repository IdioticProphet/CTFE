Vue.component('problem-button', {
	delimiters: ["!!!", "!!!"],
	data: function () {
		return {
			Button: this.unique_id,
			buttontext: "Press Me!",
		}
	},
	methods: {
		do_thing: function(variable) {
			insert_modal(variable)	
		}

	},
	props: ['unique_id'],
	template: '<button v-on:click="do_thing(Button)" class="btn btn-primary" id="Button">!!! buttontext !!!</button>',
});



Vue.component('modal-maker',{
		delimiters: ['!!!','!!!'],
		data: function() {
			return {
				items: [],
				name: null,
				summary: null,
			}
		},
		
		props: ['unique_id'],

		template: `
					
<div id="problem-modal" class="modal"  tabindex="-1" role="dialog">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="exampleModalLabel">!!! name !!!</h5>
        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
        </button>
      </div>
      <div class="modal-body">
        !!! summary !!!
      </div>
	  <form action="" method="POST" name="flag" :id ="unique_id">
      <div class="modal-footer flag-footer flag-form">
		<div class="flag-left">

		{{ form.flag(class="form-control girth", placeholder="flag") }} 
		</div><div class="flag-right">
		{{ form.submit(class="btn btn-primary", type="submit", value="Submit") }}
		<button type="button" onclick="toggle_modal()" class="btn btn-secondary flag-right">Close</button>
		</div>
		{{ form.hidden_tag() }}
		</div>
	</form>
    </div>
  </div>
</div>
	
		`,
		
		created: function() {
			this.fetchData(this.unique_id);
		},
		
		methods: {
			fetchData: function(button_id) {
				var self = this;
				fetch('./api/problems')
					.then(response => {
						var response = response.json();
						return response;
					})
					.then(json => {
						var data = json.data;
						var length = data.length;
						for (var i = 0; i<length; i++) {
							if (data[i].unique_id == button_id) {
								this.name = data[i].problem_name;
								this.summary = data[i].summary;
							}
						}
					})
				}
			},	
		});

function insert_modal(unique_id) {
	document.getElementById('modal-div').innerHTML = `<modal-maker id='problem-modal' unique_id=${unique_id}></modal-maker>`;
	new Vue({ el: `#problem-modal ` })
	toggle_modal();
}
function toggle_modal() {
$(document).ready(function(){
   $(`#problem-modal`).modal("toggle");
  });
}