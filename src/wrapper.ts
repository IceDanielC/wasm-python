import type { PyodideInterface } from "pyodide";
import { PYODIDE_SCRIPT } from "./constant";
import stitchingContent from './python/stitching.py'

class PythonWASMWrapper {
  private pyodide: PyodideInterface;

  constructor() {
    this.pyodide = null;
    // 构造时先初始化
    this.initialize();
  }

  private async initialize() {
    if (!this.pyodide) {
      // 动态加载 pyodide.js 脚本也可使用动态import
      await this.loadPyodideScript();
      // @ts-ignore
      this.pyodide = await loadPyodide();
      this.pyodide.loadPackage("opencv-python");
    }
  }

  private loadPyodideScript(): Promise<void> {
    return new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = PYODIDE_SCRIPT;
      script.onload = () => resolve();
      script.onerror = () => reject(new Error("Failed to load Pyodide"));
      document.head.appendChild(script);
    });
  }

  /**
   * 传入两个待合并图片的base64，返回合并完成图片的base64编码，前端可直接渲染
   * @param pics 图片的base64编码数组
   * @returns base64
   */
  public async picStitching(pics: string[]) {
    // 将数组转换为 Python 可以理解的格式
    const picsStr = JSON.stringify(pics);    
    await this.initialize();
    // 只是确保opencv-python完成加载，不会导致重复加载
    await this.pyodide.loadPackage("opencv-python");
    let result = "";
    try {
      // 先设置全局变量
      this.pyodide.globals.set('pics_data', picsStr);
      result = await this.pyodide.runPythonAsync(stitchingContent);
    } catch (error) {
      console.log(error);
      if (error.message?.includes("StitchingError")) {
        return "";
      }
    }

    return result;
  }
}

export default PythonWASMWrapper;
