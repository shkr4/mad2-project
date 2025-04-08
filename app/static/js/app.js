import {CustomerDashboard} from './components/cusComp.js'
import {ProfessionalDashboard} from './components/proComp.js'

const app = Vue.createApp({
    data() {
        return {
            
        }
    },
    components : {
            CustomerDashboard,
            ProfessionalDashboard,

    },
    methods: {
        func1() {
            fetch('/all_user')
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json(); // Parse the JSON response
                })
                .then(data => {
                    console.log(data); // Log the data to the console
                    this.userData = data.users; // Update userData with fetched data
                })
                .catch(error => {
                    console.error('There was a problem with the fetch operation:', error);
                });
        },
        func2() {
            if (this.userData != 'Click me for Data!') {
                this.userData = 'Click me for Data!';
            }
            else {
                this.func1();
            }
        }
    },
    mounted() {
        //this.func1(); // Call func1 when the component is mounted
    }
});

//app.component('comp1', comp1);

app.mount('#app');