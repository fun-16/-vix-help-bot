using System;
using System.Diagnostics;
using System.IO;
using System.Text;

internal class Program
{
    // ==========================================
    // VIX LAUNCHER
    // ==========================================

    private const string AdminIds = "1056612289";

    // НЕ вставляй сюда настоящий токен.
    // После перевыпуска токена укажи его локально.
    private const string BotToken = "YOUR_BOT_TOKEN_HERE";

    private static void Main()
    {
        Console.OutputEncoding = Encoding.UTF8;

        Console.Title = "VIX BOT Launcher";

        while (true)
        {
            Console.Clear();

            DrawLogo();
            DrawHeader();

            Console.WriteLine();
            WriteGreen("  [1] ", false);
            Console.WriteLine("Запустить VIX Help");

            WriteGreen("  [0] ", false);
            Console.WriteLine("Выход");

            Console.WriteLine();
            WriteGreen("  > ", false);

            string? choice = Console.ReadLine()?.Trim();

            switch (choice)
            {
                case "1":
                    LaunchBot();
                    break;

                case "0":
                    return;

                default:
                    WriteError("Неверный выбор.");
                    Pause();
                    break;
            }
        }
    }

    // ==========================================
    // ЛОГОТИП
    // ==========================================

    private static void DrawLogo()
    {
        Console.ForegroundColor = ConsoleColor.Green;

        Console.WriteLine();
        Console.WriteLine("                 ██╗   ██╗██╗██╗  ██╗");
        Console.WriteLine("                 ██║   ██║██║╚██╗██╔╝");
        Console.WriteLine("                 ██║   ██║██║ ╚███╔╝ ");
        Console.WriteLine("                 ╚██╗ ██╔╝██║ ██╔██╗ ");
        Console.WriteLine("                  ╚████╔╝ ██║██╔╝ ██╗");
        Console.WriteLine("                   ╚═══╝  ╚═╝╚═╝  ╚═╝");
        Console.WriteLine();
        Console.WriteLine("                 ██████╗  ██████╗ ████████╗");
        Console.WriteLine("                 ██╔══██╗██╔═══██╗╚══██╔══╝");
        Console.WriteLine("                 ██████╔╝██║   ██║   ██║");
        Console.WriteLine("                 ██╔══██╗██║   ██║   ██║");
        Console.WriteLine("                 ██████╔╝╚██████╔╝   ██║");
        Console.WriteLine("                 ╚═════╝  ╚═════╝    ╚═╝");

        Console.ResetColor();
    }

    // ==========================================
    // ЗАГОЛОВОК
    // ==========================================

    private static void DrawHeader()
    {
        Console.ForegroundColor = ConsoleColor.DarkGreen;

        Console.WriteLine();
        Console.WriteLine("  ═════════════════════════════════════════════");
        Console.WriteLine("                VIX BOT LAUNCHER");
        Console.WriteLine("  ═════════════════════════════════════════════");

        Console.ResetColor();
    }

    // ==========================================
    // ЗАПУСК БОТА
    // ==========================================

    private static void LaunchBot()
    {
        Console.Clear();

        DrawLogo();

        Console.WriteLine();
        WriteGreen("  VIX Help", true);
        Console.WriteLine();
        Console.WriteLine();

        // --------------------------------------
        // ПРОКСИ
        // --------------------------------------

        Console.Write("  Нужен прокси? [Y/N]: ");

        string? proxyAnswer = Console.ReadLine()?.Trim().ToLower();

        string? proxy = null;

        if (proxyAnswer == "y" ||
            proxyAnswer == "yes" ||
            proxyAnswer == "д" ||
            proxyAnswer == "да")
        {
            Console.WriteLine();

            Console.Write("  IP прокси: ");
            string? ip = Console.ReadLine()?.Trim();

            Console.Write("  PORT: ");
            string? port = Console.ReadLine()?.Trim();

            if (string.IsNullOrWhiteSpace(ip) ||
                string.IsNullOrWhiteSpace(port))
            {
                WriteError("IP или порт не указаны.");
                Pause();
                return;
            }

            proxy = $"socks5://{ip}:{port}";
        }

        Console.WriteLine();

        // --------------------------------------
        // ПОИСК EXE
        // --------------------------------------

        string launcherDirectory =
            AppContext.BaseDirectory;

        string exePath =
            Path.Combine(
                launcherDirectory,
                "vix-bot-help.exe"
            );

        if (!File.Exists(exePath))
        {
            WriteError(
                "vix-bot-help.exe не найден."
            );

            Console.WriteLine();
            Console.WriteLine(
                "Помести vix-bot-help.exe рядом с этим Launcher.exe."
            );

            Pause();
            return;
        }

        // --------------------------------------
        // ENVIRONMENT VARIABLES
        // --------------------------------------

        if (BotToken == "YOUR_BOT_TOKEN_HERE")
        {
            WriteError(
                "BOT_TOKEN не настроен."
            );

            Console.WriteLine();
            Console.WriteLine(
                "Укажи новый токен в BotToken."
            );

            Pause();
            return;
        }

        var startInfo = new ProcessStartInfo
        {
            FileName = exePath,

            // Важно:
            // users.json и admins.json бота
            // будут находиться рядом с EXE.
            WorkingDirectory = launcherDirectory,

            UseShellExecute = false,

            CreateNoWindow = false
        };

        // --------------------------------------
        // ПЕРЕДАЁМ НАСТРОЙКИ БОТУ
        // --------------------------------------

        startInfo.Environment["BOT_TOKEN"] = BotToken;
        startInfo.Environment["ADMIN_IDS"] = AdminIds;

        if (!string.IsNullOrWhiteSpace(proxy))
        {
            startInfo.Environment["BOT_PROXY"] = proxy;
        }
        else
        {
            // Если прокси не выбран —
            // гарантированно убираем переменную.
            startInfo.Environment.Remove("BOT_PROXY");
        }

        // --------------------------------------
        // ИНФОРМАЦИЯ
        // --------------------------------------

        WriteGreen("  Запуск VIX Help...", true);

        Console.WriteLine();

        Console.Write("  Администратор: ");
        WriteGreen(AdminIds, false);

        Console.WriteLine();

        Console.Write("  Прокси: ");

        if (string.IsNullOrWhiteSpace(proxy))
        {
            WriteGreen("отключён", false);
        }
        else
        {
            WriteGreen(proxy, false);
        }

        Console.WriteLine();
        Console.WriteLine();

        // --------------------------------------
        // START
        // --------------------------------------

        try
        {
            Process.Start(startInfo);

            WriteSuccess(
                "VIX Help успешно запущен."
            );
        }
        catch (Exception ex)
        {
            WriteError(
                "Ошибка запуска VIX Help:"
            );

            Console.WriteLine(ex.Message);
        }

        Console.WriteLine();
        Console.WriteLine(
            "Нажми любую клавишу для возврата в меню..."
        );

        Console.ReadKey(true);
    }

    // ==========================================
    // ЦВЕТНОЙ ВЫВОД
    // ==========================================

    private static void WriteGreen(
        string text,
        bool bold
    )
    {
        Console.ForegroundColor = ConsoleColor.Green;

        if (bold)
        {
            Console.WriteLine(text);
        }
        else
        {
            Console.Write(text);
        }

        Console.ResetColor();
    }

    private static void WriteSuccess(string text)
    {
        Console.ForegroundColor = ConsoleColor.Green;
        Console.WriteLine($"  ✓ {text}");
        Console.ResetColor();
    }

    private static void WriteError(string text)
    {
        Console.ForegroundColor = ConsoleColor.Red;
        Console.WriteLine($"  ✗ {text}");
        Console.ResetColor();
    }

    private static void Pause()
    {
        Console.WriteLine();
        Console.WriteLine(
            "Нажмите любую клавишу..."
        );

        Console.ReadKey(true);
    }
}
