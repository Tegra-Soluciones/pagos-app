import { createApp } from "vue";
import { createPinia } from "pinia";
import { frappeRequest, resourcesPlugin } from "frappe-ui";
import router from "./router";
import App from "./App.vue";
import "./index.css";

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);
app.use(resourcesPlugin);

app.mount("#app");
