export interface Config {
  app: {
    theme: string;
    output_dir: string;
    ffmpeg_path: string | null;
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
        start_task(
          video_path: string,
          target_lang: string
        ): Promise<{ status: string; message?: string }>;
        minimize(): void;
        close(): void;
        get_position(): Promise<{ x: number; y: number }>;
        move_window(x: number, y: number): void;
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
  async getConfig(): Promise<Config> {
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
    targetLang: string = "Chinese"
  ): Promise<any> {
    await waitForBridge();
    return await window.pywebview.api.start_task(videoPath, targetLang);
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
};
