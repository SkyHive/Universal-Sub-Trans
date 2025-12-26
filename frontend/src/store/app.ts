import { defineStore } from "pinia";
import { bridge, type Config, type Segment } from "../api/bridge";

export const useAppStore = defineStore("app", {
  state: () => ({
    config: null as Config | null,
    isProcessing: false,
    currentProgress: 0,
    statusMessage: "",
    results: [] as Segment[],
    systemStatus: {
      gpu_vendor: "unknown",
      can_accelerate: false,
      needs_install: false,
      install_progress: 0,
      is_installing: false,
    },
  }),
  actions: {
    async checkSystemStatus() {
      const status = await bridge.checkDepStatus();
      this.systemStatus = {
        ...this.systemStatus,
        gpu_vendor: status.gpu_vendor,
        can_accelerate: status.can_accelerate,
        needs_install: status.needs_install,
      };
    },
    async installDependencies() {
      this.systemStatus.is_installing = true;
      this.systemStatus.install_progress = 0;
      await bridge.installDeps();
    },
    updateInstallProgress(progress: number) {
      this.systemStatus.install_progress = progress;
    },
    completeInstallation(message: string) {
      this.systemStatus.is_installing = false;
      this.systemStatus.needs_install = false;
      this.systemStatus.install_progress = 100;
      this.statusMessage = message;
    },
    installationFailed(message: string) {
      this.systemStatus.is_installing = false;
      this.statusMessage = message;
    },
    async fetchConfig() {
      this.config = await bridge.fetchConfig();
    },
    async saveConfig(updates: any) {
      const resp = await bridge.updateConfig(updates);
      if (resp.status === "success") {
        this.config = resp.config;
      }
    },
    async startTask(
      videoPath: string,
      targetLang: string = "Chinese",
      resumeMode: string = "fresh"
    ) {
      this.isProcessing = true;
      this.currentProgress = 0;
      this.statusMessage = "Starting...";
      // Only clear results if it's not a resume of translation
      if (resumeMode === "fresh") {
        this.results = [];
      }
      return await bridge.startTask(videoPath, targetLang, resumeMode);
    },

    async checkResumePoint(path: string) {
      return await bridge.checkResumePoint(path);
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
