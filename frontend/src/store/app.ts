import { defineStore } from "pinia";
import { bridge, type Config, type Segment } from "../api/bridge";

export const useAppStore = defineStore("app", {
  state: () => ({
    config: null as Config | null,
    isProcessing: false,
    currentProgress: 0,
    statusMessage: "",
    currentStage: "idle", // idle, loading_model, transcribing, translating, saving, installing, cancelling
    results: [] as Segment[],
    systemStatus: {
      gpu_vendor: "unknown",
      can_accelerate: false,
      needs_install: false,
      install_progress: 0,
      is_installing: false,
    },
  }),
  getters: {
    buttonText: (state) => {
      switch (state.currentStage) {
        case "loading_model":
          return "Loading AI Model...";
        case "transcribing":
          return "Transcribing Audio...";
        case "translating":
          return "Translating Text...";
        case "saving":
          return "Saving Results...";
        case "cancelling":
          return "Cancelling...";
        case "installing":
          return "Installing...";
        default:
          return "Start Production";
      }
    },
  },
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
      this.currentStage = "installing";
      this.statusMessage = "Starting installation...";
      await bridge.installDeps();
    },
    updateInstallProgress(data: {
      progress: number;
      message: string;
      stage?: string;
    }) {
      this.systemStatus.install_progress = data.progress;
      if (data.message) {
        this.statusMessage = data.message;
      }
      if (data.stage) {
        this.currentStage = data.stage;
      }
    },
    completeInstallation(message: string) {
      this.systemStatus.is_installing = false;
      this.systemStatus.needs_install = false;
      this.systemStatus.install_progress = 100;
      this.currentStage = "idle";
      this.statusMessage = message;
    },
    installationFailed(message: string) {
      this.systemStatus.is_installing = false;
      this.currentStage = "idle";
      this.statusMessage = message;
    },
    async cancelCurrentTask() {
      if (this.isProcessing) {
        this.statusMessage = "Cancelling...";
        this.currentStage = "cancelling";
        await bridge.cancelTask();
      }
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
      this.currentStage = "loading_model";
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

    updateStatus(data: { message: string; progress: number; stage?: string }) {
      this.statusMessage = data.message;
      this.currentProgress = data.progress;
      if (data.stage) {
        this.currentStage = data.stage;
      }
    },
    completeTask(data: { segments: Segment[] }) {
      this.results = data.segments;
      this.isProcessing = false;
      this.currentProgress = 100;
      this.currentStage = "idle";
      this.statusMessage = "Task completed successfully.";
    },
    taskFailed(data: { message: string; cancelled?: boolean }) {
      this.isProcessing = false;
      this.currentStage = "idle";
      if (data.cancelled) {
        this.statusMessage = "Task cancelled by user.";
      } else {
        this.statusMessage = `Error: ${data.message}`;
      }
    },
  },
});
