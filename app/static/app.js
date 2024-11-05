const app = Vue.createApp({
    data() {
        return {
            name: "Shekhar",
            userData: null  // Store fetched data here
        }
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
        }
    },
    mounted() {
        this.func1(); // Call func1 when the component is mounted
    }
});

app.mount('#app');