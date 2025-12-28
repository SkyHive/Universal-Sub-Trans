export interface Config {
  app: {
    theme: string;
    output_dir: string;
    pypi_mirror: string;
    language: string;
    log_level: string;
  };
  whisper: {
    model_size: string;
    device: string;
    compute_type: string;
    language: string | null;
  };
  ai: {
    api_key: string;
    base_url: string;
    model_name: string;
    temperature: number;
    batch_size: number;
    system_prompt: string;
    fallback_prompt: string;
  };
}

export interface TaskStatus {
  message: string;
  progress: number;
}

export interface Segment {
  start: number;
  end: number;
  text: string;
  translated_text?: string;
}

declare global {
  interface Window {
    pywebview: {
      api: {
        get_config(): Promise<Config>;
        update_config(
          updates: Partial<Config>
        ): Promise<{ status: string; config: Config }>;
        select_file(): Promise<string | null>;
        check_task_resume_point(video_path: string): Promise<{
          has_audio: boolean;
          has_transcript: boolean;
        }>;
        start_task(
          video_path: string,
          target_lang: string,
          resume_mode: string
        ): Promise<{ status: string; message?: string }>;
        minimize(): void;
        close(): void;
        get_position(): Promise<{ x: number; y: number }>;
        move_window(x: number, y: number): void;
        get_size(): Promise<{ width: number; height: number }>;
        resize_window(width: number, height: number): void;
        cancel_task(): Promise<{ status: string }>;
        check_dep_status(): Promise<{
          gpu_vendor: string;
          can_accelerate: boolean;
          needs_install: boolean;
        }>;
        install_deps(): Promise<{ status: string }>;
        get_app_paths(): Promise<{
          config: string;
          logs: string;
          libs: string;
        }>;
        open_path(
          path_type: string
        ): Promise<{ status: string; message?: string }>;
        get_app_info(): Promise<{ version: string; name: string }>;
      };
    };
    onBackendEvent: (event: string, data: any) => void;
  }
}

const waitForBridge = (): Promise<void> => {
  return new Promise((resolve) => {
    const isReady = () => {
      // Check if pywebview and the api are initialized AND the specific method exists
      return !!(
        window.pywebview &&
        window.pywebview.api &&
        typeof window.pywebview.api.get_config === "function"
      );
    };

    if (isReady()) {
      resolve();
      return;
    }

    // Try multiple ways to detect readiness
    const checkInterval = setInterval(() => {
      if (isReady()) {
        clearInterval(checkInterval);
        resolve();
      }
    }, 100);

    window.addEventListener(
      "pywebviewready",
      () => {
        if (isReady()) {
          clearInterval(checkInterval);
          resolve();
        }
      },
      { once: true }
    );

    // Safety timeout - resolve anyway after 5 seconds to avoid infinite hangs,
    // but the actual call might still fail if still not ready.
    setTimeout(() => {
      clearInterval(checkInterval);
      resolve();
    }, 5000);
  });
};

export const bridge = {
  async fetchConfig(): Promise<Config> {
    await waitForBridge();
    if (!window.pywebview?.api?.get_config) {
      console.error(
        "Bridge Error: get_config not found. Available methods:",
        window.pywebview?.api ? Object.keys(window.pywebview.api) : "None"
      );
      throw new Error("Bridge method get_config not found");
    }
    return await window.pywebview.api.get_config();
  },

  async updateConfig(updates: any): Promise<any> {
    await waitForBridge();
    return await window.pywebview.api.update_config(updates);
  },

  async selectFile(): Promise<string | null> {
    await waitForBridge();
    return await window.pywebview.api.select_file();
  },

  async startTask(
    videoPath: string,
    targetLang: string = "Chinese",
    resumeMode: string = "fresh"
  ): Promise<any> {
    await waitForBridge();
    return await window.pywebview.api.start_task(
      videoPath,
      targetLang,
      resumeMode
    );
  },

  async minimize(): Promise<void> {
    await waitForBridge();
    window.pywebview.api.minimize();
  },

  async close(): Promise<void> {
    await waitForBridge();
    window.pywebview.api.close();
  },

  async getPosition(): Promise<{ x: number; y: number }> {
    await waitForBridge();
    return await window.pywebview.api.get_position();
  },

  async moveWindow(x: number, y: number): Promise<void> {
    await waitForBridge();
    window.pywebview.api.move_window(x, y);
  },

  async getSize(): Promise<{ width: number; height: number }> {
    await waitForBridge();
    return await window.pywebview.api.get_size();
  },

  async resizeWindow(width: number, height: number): Promise<void> {
    await waitForBridge();
    window.pywebview.api.resize_window(width, height);
  },

  async cancelTask(): Promise<any> {
    await waitForBridge();
    return await window.pywebview.api.cancel_task();
  },

  async checkDepStatus(): Promise<any> {
    await waitForBridge();
    return await window.pywebview.api.check_dep_status();
  },

  async checkResumePoint(videoPath: string): Promise<any> {
    await waitForBridge();
    return await window.pywebview.api.check_task_resume_point(videoPath);
  },

  async installDeps(): Promise<any> {
    await waitForBridge();
    return await window.pywebview.api.install_deps();
  },

  async getAppPaths(): Promise<{ config: string; logs: string; libs: string }> {
    await waitForBridge();
    return await window.pywebview.api.get_app_paths();
  },

  async openPath(pathType: string): Promise<any> {
    await waitForBridge();
    return await window.pywebview.api.open_path(pathType);
  },

  async getAppInfo(): Promise<{ version: string; name: string }> {
    await waitForBridge();
    return await window.pywebview.api.get_app_info();
  },
};
