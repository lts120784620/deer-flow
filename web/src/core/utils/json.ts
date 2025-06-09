import { parse } from "best-effort-json-parser";

export function parseJSON<T>(json: string | null | undefined, fallback: T) {
  if (!json) {
    return fallback;
  }
  
  try {
    let raw = json.trim();
    
    // 检查是否是异常信息，直接返回 fallback
    if (raw.startsWith('Exception(') || raw.startsWith('Error:') || raw.startsWith('Traceback')) {
      console.warn("Content appears to be an error message, returning fallback:", raw.substring(0, 100));
      return fallback;
    }
    
    // 清理 markdown 代码块
    raw = raw
      .replace(/^```json\s*/, "")
      .replace(/^```\s*/, "")
      .replace(/\s*```$/, "");
    
    // 清理可能存在的额外 tokens 和格式问题
    raw = raw
      .replace(/^\{+/g, "{")  // 移除开头多余的 {
      .replace(/\}+$/g, "}")  // 移除结尾多余的 }
      .replace(/\}\s*\{/g, "},{")  // 修复连续的对象
      .replace(/,\s*}/g, "}")  // 移除尾随逗号
      .replace(/,\s*]/g, "]"); // 移除数组尾随逗号
    
    // 如果内容为空或仅包含空白字符，返回 fallback
    if (!raw || raw.trim() === "" || raw === "{}" || raw === "[]") {
      return fallback;
    }
    
    // 首先尝试标准 JSON.parse，这样更快且更可靠
    try {
      return JSON.parse(raw) as T;
    } catch (parseError) {
      console.warn("Standard JSON.parse failed, trying best-effort parser:", parseError);
      // 如果标准解析失败，尝试使用 best-effort-json-parser
      // 但是先进行额外的清理来处理 extra tokens 问题
      const extraCleanedRaw = cleanExtraTokens(raw);
      try {
        return parse(extraCleanedRaw) as T;
      } catch (bestEffortError) {
        console.warn("Best-effort JSON parsing also failed:", bestEffortError, "Original content:", json);
        return fallback;
      }
    }
  } catch (error) {
    console.warn("JSON parsing completely failed:", error, "Original content:", json);
    return fallback;
  }
}

function cleanExtraTokens(jsonString: string): string {
  // 更激进的清理，专门处理 extra tokens 问题
  let cleaned = jsonString.trim();
  
  // 移除任何非 JSON 字符序列
  cleaned = cleaned.replace(/^[^{\[]*/, ""); // 移除开头非JSON字符
  cleaned = cleaned.replace(/[^}\]]*$/, ""); // 移除结尾非JSON字符
  
  // 处理常见的 extra tokens 问题
  cleaned = cleaned.replace(/\{\}/g, "null"); // 将空对象替换为 null
  cleaned = cleaned.replace(/\{\s*\}/g, "null"); // 将只包含空白的对象替换为 null
  
  // 如果结果为空或只是 null，返回空数组字符串（适合大多数使用场景）
  if (!cleaned || cleaned === "null" || cleaned === "undefined") {
    return "[]";
  }
  
  return cleaned;
}
