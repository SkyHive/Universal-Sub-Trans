import { defineStore } from "pinia";
import { bridge, type Config, type Segment } from "../api/bridge";

export const useAppStore = defineStore("app", {
  state: () => ({
    config: null as Config | null,
    isProcessing: false,
    currentProgress: 0,
    statusMessage: "",
    results: [] as Segment[],
  }),
  actions: {
    async fetchConfig() {
      this.config = await bridge.getConfig();
    },
    async saveConfig(updates: any) {
      const resp = await bridge.updateConfig(updates);
      if (resp.status === "success") {
        this.config = resp.config;
      }
    },
    async startTask(videoPath: string, targetLang: string) {
      this.results = [];
      const resp = await bridge.startTask(videoPath, targetLang);
      if (resp.status === "started") {
        this.isProcessing = true;
      }
      return resp;
    },
    updateStatus(data: { message: string; progress: number }) {
      this.statusMessage = data.message;
      this.currentProgress = data.progress;
    },
    completeTask(data: { segments: Segment[] }) {
      this.results = data.segments;
      this.isProcessing = false;
      this.currentProgress = 100;
      this.statusMessage = "Task completed successfully.";
    },
    taskFailed(data: { message: string }) {
      this.isProcessing = false;
      this.statusMessage = `Error: ${data.message}`;
    },
  },
});
