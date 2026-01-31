// ===============================
// 🤖 Auto Edit Selected Files Only
// Работает через Hugging Face Space API
// ===============================

const fetch = require("node-fetch");
const fs = require("fs");
const { execSync } = require("child_process");

const API_URL = "https://NekitWlk-auto-edit-bot.hf.space/api/edit"; // 👈 твой Space URL

// Только эти файлы
const FILES = ["script.js", "index.html", "style.css"];

async function editFile(filePath) {
  if (!fs.existsSync(filePath)) {
    console.log(`⚠️ Файл ${filePath} не найден, пропускаю.`);
    return;
  }

  const content = fs.readFileSync(filePath, "utf8");

  // Если файл пустой или слишком большой, пропускаем
  if (content.length < 10) {
    console.log(`⚠️ ${filePath} пустой, пропускаю.`);
    return;
  }
  if (content.length > 8000) {
    console.log(`⚠️ ${filePath} слишком большой (${content.length} символов), пропускаю.`);
    return;
  }

  const prompt = `
Ты — AI-редактор кода. Улучши форматирование и читаемость файла, не меняя поведение программы.
Файл: ${filePath}
Содержимое:
${content}
`;

  console.log(`📡 Отправляю ${filePath}...`);
  const res = await fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt }),
  });

  if (!res.ok) {
    console.log(`⚠️ Пропускаю ${filePath}: Ошибка API ${res.status}`);
    return;
  }

  const data = await res.json();
  const newText = data.text || content;

  fs.writeFileSync(filePath, newText, "utf8");
  console.log(`💾 ${filePath} успешно обновлён!`);
}

(async () => {
  try {
    console.log("🚀 Запускаю авто-редактирование...");

    for (const file of FILES) {
      await editFile(file);
    }

    // Коммитим и пушим
    execSync('git config user.email "github-actions[bot]@users.noreply.github.com"');
    execSync('git config user.name "github-actions[bot]"');
    execSync("git add script.js index.html style.css");
    execSync('git commit -m "🤖 Auto-edit selected files via HF Space" || echo "⚠️ Нет изменений для коммита"');
    execSync("git push");

    console.log("✅ Готово! Изменения отправлены в репозиторий.");
  } catch (e) {
    console.error("❌ Ошибка:", e.message);
    process.exit(1);
  }
})();
