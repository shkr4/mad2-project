export const CustomerDashboard = {
  template : `<div style="background-color: aliceblue; padding: 15px;">

                  <h1>Dashboard of Customer: {{comp_name}}</h1>                
                  <h4>Customer Username: {{comp_username}}</h4>
                  <h5>Customer Email: {{comp_email}}</h5>
                  <h3>Search For a Service</h3><input type="text" v-model="inputValue" placeholder="Service Name">
                  <button @click="sendData">Search</button><br>
                  <p>You are Typing: <b>{{ inputValue }}</b></p>

                  
                 
              </div>
              <div v-if="serviceFound">
              <div>
                <h5>Searched Result for query: {{ inputValue }}</h5>
              </div>  
                <table>
                  <thead>
                    <tr>
                      <th>Service Name</th>
                      <th>Price</th>
                      <th>Service Provider</th>
                      <th>Overall Rating</th>
                      <th>Service Description</th>
                      <th>Address</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="service in serviceFound" :key="service['Professional ID']">
                      <td>{{ service['Service Name'] }}</td>
                      <td>{{ service['Price'] }}</td>
                      <td>{{ service['Service Provider'] }}</td>
                      <td>{{ service['Rating'] }}</td>
                      <td>{{ service['Service Description'] }}</td>
                      <td>{{ service['Address'] }}</td>
                      <td><button @click="placeOrder({user_id: comp_id, professional_id: service['Professional ID'],
                      service: service['Service Name']})">Book</button><br></td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <h3>Your Placed Orders</h3>

                  <div class="table-container">
                     
                     <table>
                      <thead>
                        <tr>                     
                            <th>Order ID</th>
                            <th>Service</th>                        
                            <th>Professional Name</th>
                            <th>Professional Address</th>
                            <th>Status</th>
                            <th>Rating</th>
                            <th>Booked At</th>
                            <th>Accepted At</th>
                            <th>Closed At</th>
                            <th>Closed By</th>
                            <th>Feedback</th>
                            <th>Action</th>
                        </tr>
                      </thead>
                     <tbody>
                      <tr v-for="order in comp_orders">
                          <td>{{order.order_id}}</td>
                          <td>{{order.services}}</td>
                          
                          <td>{{order.pro_name}}</td>
                          <td>{{order.pro_add}}</td>
                          <td>{{order.status}}</td>
                          
                          <td v-if="order.status === 'accepted'">
                          <input v-model="order.rating" placeholder="Between 1 to 5" min="1" max="5" required type="number"></td>
                          <td v-else>{{ order.rating }}</td>
                          
                          <td>{{order.booked_at}}</td>
                          <td>{{order.accepted_at}}</td>
                          <td>{{order.closed_at}}</td>
                          <td>{{order.closed_by}}</td>                          
                          <td v-if="order.status === 'accepted'">
                          <input v-model="order.remark_by_customer" type="text" required></td>
                          <td v-else-if="order.status === 'closed'">{{ order.remark_by_customer }}</td>

                          <td v-if="order.status === 'requested'">
                          <button @click="cancelOrder(order.order_id)">Cancel Order</button> </td>
                          <td v-else-if="order.status === 'accepted'">
                          <button @click="closeOrder(order)">Close Order</button> </td>
                         
                      </tr>
                     </tbody>

    
                     </table>
                     
                  </div>
                 
                
              
`,
  props: ["current_user"],
  data(){
    return {

      comp_username: this.current_user.username,
      comp_address: this.current_user.address,
      comp_email: this.current_user.email,
      comp_id: this.current_user.id,
      comp_name: this.current_user.name,
      comp_role: this.current_user.role,
      comp_orders: null,
      inputValue: '',
      serviceFound: null,
      cusRating: null,
      cusFeedback: null,
      
    }
  },
  methods: {
    async closeOrder(order) {
      try {
          const response = await fetch('/v_close_order', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                  order_id: order.order_id,
                  cusRating: order.rating,
                  
                  cusFeedback: order.remark_by_customer
              })
          });

          if (response.ok) {
            const data2 = await response.json()
              console.log(`Order ${order.order_id} closed successfully`);
              order.status = "closed";
              order.closed_at = data2['time'];
              order.closed_by = "customer";// Update UI to remove inputs
          } else {
              console.error("Failed to close order");
          }
      } catch (error) {
          console.error("Error submitting feedback:", error);
      }
  },
      getOrders(){
        fetch(`/get_orders_of_user_id/${this.comp_id}`)
        .then(res => {return res.json()})  // Convert response to JSON
        .then(data => {this.comp_orders = data})    // Handle the data
        .catch(error => console.error("Error:", error));
      },
      async sendData() {
        const data = { value: this.inputValue };

        try {
            const res = await fetch("/v_find_service", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });

            const result = await res.json();
            this.serviceFound = result; // Update response message
        } catch (error) {
            console.error("Error:", error);
        }
    },
    async placeOrder({user_id, professional_id, service}){

      const data = {user_id: user_id, professional_id: professional_id, service: service}
      console.log(data)

      try {
        const res = await fetch("/v_place_order", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });
        this.getOrders();
      } catch (error) {
          console.error("Error:", error);
      }

    },
    async cancelOrder(order_id){
      const data = {order_id:order_id}
      try{
        const res = await fetch("/v_cancel_order",{
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify(data)
        });
        const resData = await res.json()
        console.log(resData['message'])
        //this.getOrders();
        const order = this.comp_orders.find(o => o.order_id === order_id)
                if (order) {
                    order.status = "cancelled";  // Update status in UI
                }
                else {
                console.error("Failed to cancel order");
              }
        }catch(error){
        console.error("Error:", error);
      }
    }
  },
  mounted() {
    this.getOrders();
  }
};
