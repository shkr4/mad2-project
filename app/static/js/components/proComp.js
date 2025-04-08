export const ProfessionalDashboard = {
  template: `<div style="background-color: aliceblue; padding: 15px;">

                  <h1>Dashboard of Professional: {{comp_name}}</h1>                
                  <h4>Customer Username: {{comp_username}}</h4>
                  <h5>Customer Email: {{comp_email}}</h5>
                  <h3>Search For a Service</h3>
                  <input type="text" v-model="inputValue" placeholder="Service Name">
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
                    <td><button @click="placeOrder({user_id: comp_id, professional_id: service['Professional ID'], service: service['Service Name']})">Book</button><br></td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div v-if="pro_data">
              <h2>Order Placed to You</h2>
              <div class="table-container">
                  <table>
                      <thead>
                          <tr>
                              <th>Order ID</th>
                              <th>Customer Name</th>
                              <th>Customer Address</th>    
                              <th>Status</th>    
                              <th>Rating</th>    
                              <th>Booked At</th>    
                              <th>Closed At</th>    
                              <th>Accepted At</th>    
                              <th>Closed By</th>    
                              <th>Feedback By Customer</th>
                              <th>Action</th>   
                          </tr>
                      </thead>
                      <tbody>
                          <tr v-for="order in pro_data">
                              <td>{{order.order_id}}</td>
                              <td>{{order.customer_name}}</td>
                              <td>{{order.customer_address}}</td>
                              <td>{{order.status}}</td>
                              <td>{{order.rating}}</td>
                              <td>{{order.booked_at}}</td>
                              <td>{{order.closed_at}}</td>
                              <td>{{order.accepted_at}}</td>
                              <td>{{order.closed_by}}</td>
                              <td>{{order.remark_by_customer}}</td>
                              <td>
                                  <button @click="v_accept_it(order.order_id)" v-if="order.status === 'requested'">Accept</button>
                                  <button @click="v_reject_it(order.order_id)" v-if="order.status === 'requested'">Reject</button>
                              </td>
                          </tr>
                      </tbody>
                  </table>
              </div>
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
                            <th>Feedback Given</th>
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
                          <td>{{order.rating}}</td>
                          <td>{{order.booked_at}}</td>
                          <td>{{order.accepted_at}}</td>
                          <td>{{order.closed_at}}</td>
                          <td>{{order.closed_by}}</td>
                          <td>{{order.remark_by_customer}}</td>
                          <td v-if="order.status === 'requested'">
                          <button @click="cancelOrder(order.order_id)">Cancel Order</button> </td>
                      </tr>
                     </tbody>
                    </table>
                     
                  </div>
                <h3>Services Offered By Me</h3>
                <div class="table-container">
                  <table>
                          <thead>
                            <tr>
                              <th>Service Name</th>
                              <th>Price</th>
                              <th>Description</th>
                              <th>Action</th>
                            </tr>
                          </thead>
                          <tbody>
                            <tr v-for="service in comp_pro_services">
                              <td>{{ service.service }}</td>
                              <td>{{ service.price }}</td>
                              <td>{{ service.description }}</td>
                              <td><button @click="deleteService(service.id, service.service)">Delete</button></td>
                            </tr>
                          </tbody>
                        </table>
                </div>       
                      
                <h3>Services Offered By the Company<h3>
                <div class="table-container">
                        <table>
                          <thead>
                            <tr>
                              <td>Service Name</td>
                              <td>Description</td>
                              <td>Price</td>
                              <td>Action</td>
                            </tr>
                          </thead>
                          <tbody>
                            <tr v-for="service in comp_company_services" :key="service.id">
                              <td>{{ service.name }}</td>
                              <td> <input :ref="'des_' + service.id" name="des" type="text" required></td>
                              <td> <input :ref="'price_' + service.id" name="price" type="number" required></td>
                              <td>
                                <button @click="addThisService(service.id, service.name)">Add This service</button>
                              </td>
                            </tr>
                          </tbody>
                        </table>                     
                </div>
                 
                
              
`,
  props: ["current_user"],
  data(){
    return{
      comp_username: this.current_user.username,
      comp_address: this.current_user.address,
      comp_email: this.current_user.email,
      comp_id: this.current_user.id,
      comp_name: this.current_user.name,
      comp_role: this.current_user.role,
      comp_orders: [], //null,
      inputValue: '',
      serviceFound: null,
      pro_data: [], //null,
      comp_pro_services: [],
      comp_company_services: [],
    }
  },
  methods: {
    async deleteService(s_id, name){
      console.log(s_id, name)
      const res = await fetch('/v_delete_pro_service',{
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ service_id: s_id, serviceName: name })
      })
      if (res.ok){
        const index = this.comp_pro_services.findIndex(s => s.id === s_id);
        if (index !== -1) {
          this.comp_pro_services.splice(index, 1); // Remove the order at the found index
      }

      }
    },
    async addThisService(s_id, name){
      
        const res = await fetch('/v_add_service',{
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            service_id: s_id,
            des: this.$refs['des_' + s_id][0].value,  // Correctly accessing the input value
            price: this.$refs['price_' + s_id][0].value,
            name: name
        })
        });
        if (res.ok){
          const data2 = await res.json()
          this.comp_pro_services.push(data2)
        } 
    },
    updateOrderStatus(orderId, newStatus) {
      const order = this.pro_data.find(o => o.order_id === orderId);
      if (order) {
          order.status = newStatus;
      }
    },
    getOrders(){
      fetch(`/get_orders_of_user_id/${this.comp_id}`)
      .then(res => {return res.json()})  // Convert response to JSON
      .then(data => {this.comp_orders = data})    // Handle the data
      .catch(error => console.error("Error:", error));
    },
    v_accept_it(oid) {
      fetch(`/v_accept_it`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ order_id: oid })
      })
      .then(res => res.json())
      .then(data => console.log(`Order No. ${oid} has been accepted`))
      .catch(error => console.error("Error:", error));
      this.updateOrderStatus(oid, 'accepted');
    },
    v_reject_it(oid) {
      fetch(`/v_reject_it`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ order_id: oid })
      })
      .then(res => res.json())
      .then(data => console.log(`Order No. ${oid} has been rejected`))
      .catch(error => console.error("Error:", error));
      this.updateOrderStatus(oid, 'rejected');
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
      this.getOrders();
    }catch(error){
      console.error("Error:", error);
    }
  },
  async getProOrder(user_id){
    const data = {user_id: user_id}
    const pro_orders = await fetch('/v_pro_orders',{
      method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
    });
    const res = await pro_orders.json()
    this.pro_data = res['OrderList'];
    this.comp_company_services = res['companyService'];
    //this.comp_pro_services = res['companyService']
    this.comp_pro_services = res['serviceOfferedByPro']

  },
},
mounted() {
  this.getOrders();
  this.getProOrder(this.comp_id);
}
}
