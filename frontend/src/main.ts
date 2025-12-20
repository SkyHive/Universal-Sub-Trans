import { createApp } from "vue";
import { createPinia } from "pinia";
import "./index.css";
import App from "./App.vue";
import { useAppStore } from "./store/app";

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.mount("#app");

// Register backend event listener
const store = useAppStore(pinia);
window.onBackendEvent = (event: string, data: any) => {
  console.log("Backend event:", event, data);
  switch (event) {
    case "status_update":
      store.updateStatus(data);
      break;
    case "task_completed":
      store.completeTask(data);
      break;
    case "task_failed":
      store.taskFailed(data);
      break;
  }
};
