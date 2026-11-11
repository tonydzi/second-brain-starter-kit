/*
 * display_mode: сменить разрешение главного экрана Мака через CoreGraphics, без сторонних программ.
 *
 * Зачем на C: на Intel Mac Pro Swift-компилятор не совпадает с SDK Command Line Tools
 * (swift падает на сборке модуля CoreFoundation), displayplacer не стоит. clang есть везде,
 * где стоят Command Line Tools.
 *
 * Использование:
 *   display_mode                  текущий режим (*) и все режимы, годные для рабочего стола
 *   display_mode pick W H PW HZ   какой режим будет выбран, экран не трогает
 *   display_mode set  W H PW HZ   поставить навсегда, дождаться, сверить, напечатать откат
 *   display_mode --selftest       логика выбора и разбора чисел на таблице с ловушками (exit 0 = ок)
 *
 *   W H = размер интерфейса («UI looks like»), PW = ширина в настоящих пикселях,
 *   HZ = частота как в списке (60, 59.94; у встроенных экранов ноутбуков бывает 0).
 *   PW = 2*W: чёткий HiDPI. PW = W: настоящее низкое разрешение, видеокарте легче.
 *
 * Ловушки (Intel Mac Pro, 4K-монитор; 3-5 нашла панель внешних моделей):
 *   1. ioDisplayModeID у «1920x1080 настоящий» и у «960x540 HiDPI» один и тот же:
 *      выбор по ID ставит огромный интерфейс.
 *   2. По одной ширине 1600 находятся и 1600x900, и 1600x1200 (4:3).
 *   3. Частоты 59.94 и 60 при округлении сливаются: берём ближайшую, а не первую.
 *   4. Два режима с одной четвёркой, но разной высотой в пикселях: выбор отказывается
 *      (exit 3, «неоднозначно»), а не берёт первый попавшийся.
 *   5. Мусор в числах («60Hz», «abc») раньше становился 60 или 0: теперь exit 2.
 * После set экран перечитывается до 2 с: режим может встать не мгновенно.
 *
 * Только главный экран (CGMainDisplayID). Второй монитор не трогает.
 * CF-объекты не освобождаются намеренно: процесс живёт доли секунды.
 *
 * Сборка: clang -O2 -framework ApplicationServices -o ~/.claude/scripts/bin/display_mode display_mode.c
 */
#include <ApplicationServices/ApplicationServices.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

struct mode { size_t w, h, pw, ph; double hz; };

static int same(struct mode a, struct mode b) {
  return a.w == b.w && a.h == b.h && a.pw == b.pw && a.ph == b.ph && a.hz == b.hz;
}

/* Чистая функция выбора. Ключ W H PW точный, частота ближайшая в пределах 0.5 Гц.
 * Возврат: индекс; -1 = нет режима; -2 = неоднозначно (две строки одинаково близки). */
static int pick(const struct mode *t, int n, size_t w, size_t h, size_t pw, double hz) {
  int best = -1, ties = 0;
  double best_d = 0.5;
  for (int i = 0; i < n; i++) {
    if (t[i].w != w || t[i].h != h || t[i].pw != pw) continue;
    double d = fabs(t[i].hz - hz);
    if (d >= 0.5) continue;
    if (best < 0 || d < best_d - 1e-6) { best = i; best_d = d; ties = 0; }
    else if (fabs(d - best_d) <= 1e-6) ties++;
  }
  return ties ? -2 : best;
}

/* Строгий разбор числа: вся строка обязана быть числом >= 0. */
static int parse_num(const char *s, double *out) {
  char *end;
  if (!s || !*s) return 0;
  double v = strtod(s, &end);
  if (*end != '\0' || v < 0 || !isfinite(v)) return 0;
  *out = v;
  return 1;
}

static int selftest(void) {
  /* Порядок важен: ловушки стоят раньше правильных строк, как в живом списке CoreGraphics. */
  const struct mode t[] = {
    {1920, 1080, 3840, 2160, 60},
    { 960,  540, 1920, 1080, 60},     /* ловушка 1: тот же ID, что у настоящего 1920x1080 */
    {1920, 1080, 1920, 1080, 59.94},  /* ловушка 3: соседняя частота */
    {1920, 1080, 1920, 1080, 60},
    {1600, 1200, 1600, 1200, 60},     /* ловушка 2: та же ширина, другой формат */
    {1600,  900, 1600,  900, 60},
    {1600,  900, 3200, 1800, 60},
    {1280,  800, 1280,  800, 60},     /* ловушка 4: та же четвёрка, разная высота в пикселях */
    {1280,  800, 1280,  720, 60},
  };
  const int n = (int)(sizeof t / sizeof t[0]);
  struct { size_t w, h, pw; double hz; int want; } c[] = {
    {1920, 1080, 1920, 60,    3},
    {1920, 1080, 1920, 59.94, 2},
    {1920, 1080, 3840, 60,    0},
    {1600,  900, 1600, 60,    5},
    {1600,  900, 3200, 60,    6},
    {1280,  800, 1280, 60,   -2},
    {1234,  567, 1234, 60,   -1},
  };
  int fails = 0;
  for (size_t k = 0; k < sizeof c / sizeof c[0]; k++) {
    int i = pick(t, n, c[k].w, c[k].h, c[k].pw, c[k].hz);
    int ok = i == c[k].want;
    printf("%s pick %zux%zu px%zu @%g -> %d (ждали %d)\n", ok ? "PASS" : "FAIL",
           c[k].w, c[k].h, c[k].pw, c[k].hz, i, c[k].want);
    if (!ok) fails++;
  }
  struct { const char *s; int ok; } p[] = {
    {"60", 1}, {"59.94", 1}, {"0", 1}, {"60Hz", 0}, {"abc", 0}, {"", 0}, {"-1", 0},
  };
  for (size_t k = 0; k < sizeof p / sizeof p[0]; k++) {
    double v;
    int ok = parse_num(p[k].s, &v) == p[k].ok;
    printf("%s parse \"%s\"\n", ok ? "PASS" : "FAIL", p[k].s);
    if (!ok) fails++;
  }
  printf("%s\n", fails ? "SELFTEST FAIL" : "SELFTEST OK");
  return fails ? 1 : 0;
}

static struct mode to_mode(CGDisplayModeRef m) {
  struct mode r = { CGDisplayModeGetWidth(m), CGDisplayModeGetHeight(m),
                    CGDisplayModeGetPixelWidth(m), CGDisplayModeGetPixelHeight(m),
                    CGDisplayModeGetRefreshRate(m) };
  return r;
}

static void print_mode(const char *prefix, struct mode m) {
  printf("%s%zu %zu %zu %zu %g\n", prefix, m.w, m.h, m.pw, m.ph, m.hz);
}

static int current(CGDirectDisplayID d, struct mode *out) {
  CGDisplayModeRef m = CGDisplayCopyDisplayMode(d);
  if (!m) return 0;
  *out = to_mode(m);
  CGDisplayModeRelease(m);
  return 1;
}

int main(int argc, char **argv) {
  if (argc > 1 && strcmp(argv[1], "--selftest") == 0) return selftest();

  size_t w = 0, h = 0, pw = 0;
  double hz = 0;
  int want_set = 0;
  if (argc != 1) {
    double a, b, c;
    if (argc != 6 || (strcmp(argv[1], "pick") != 0 && strcmp(argv[1], "set") != 0) ||
        !parse_num(argv[2], &a) || !parse_num(argv[3], &b) || !parse_num(argv[4], &c) ||
        !parse_num(argv[5], &hz) || a < 1 || b < 1 || c < 1 ||
        a != floor(a) || b != floor(b) || c != floor(c)) {
      fprintf(stderr, "usage: display_mode | display_mode pick|set W H PW HZ | display_mode --selftest\n");
      return 2;
    }
    w = (size_t)a; h = (size_t)b; pw = (size_t)c;
    want_set = strcmp(argv[1], "set") == 0;
  }

  CGDirectDisplayID d = CGMainDisplayID();
  const void *k[] = { kCGDisplayShowDuplicateLowResolutionModes };
  const void *v[] = { kCFBooleanTrue };
  CFDictionaryRef o = CFDictionaryCreate(NULL, k, v, 1, &kCFTypeDictionaryKeyCallBacks,
                                         &kCFTypeDictionaryValueCallBacks);
  CFArrayRef all = CGDisplayCopyAllDisplayModes(d, o);
  struct mode cur;
  if (!all || !current(d, &cur)) {
    fprintf(stderr, "нет доступа к экрану (нет графической сессии или экран отключён)\n");
    return 1;
  }
  CFIndex total = CFArrayGetCount(all);

  /* Только годные для рабочего стола, без точных дублей. refs[i] соответствует t[i]. */
  struct mode *t = calloc((size_t)total + 1, sizeof *t);
  CGDisplayModeRef *refs = calloc((size_t)total + 1, sizeof *refs);
  if (!t || !refs) { fprintf(stderr, "нет памяти\n"); return 1; }
  int n = 0;
  for (CFIndex i = 0; i < total; i++) {
    CGDisplayModeRef m = (CGDisplayModeRef)CFArrayGetValueAtIndex(all, i);
    if (!CGDisplayModeIsUsableForDesktopGUI(m)) continue;
    struct mode x = to_mode(m);
    int dup = 0;
    for (int j = 0; j < n && !dup; j++) dup = same(t[j], x);
    if (dup) continue;
    t[n] = x; refs[n] = m; n++;
  }

  if (argc == 1) {
    printf("#  W    H    PW   PH   HZ   (W H = интерфейс, PW PH = пиксели, * = сейчас)\n");
    for (int i = 0; i < n; i++) print_mode(same(t[i], cur) ? "* " : "  ", t[i]);
    return 0;
  }

  int i = pick(t, n, w, h, pw, hz);
  if (i == -2) {
    fprintf(stderr, "неоднозначно: несколько режимов %zu %zu %zu %g, смотри список: display_mode\n", w, h, pw, hz);
    return 3;
  }
  if (i < 0) {
    fprintf(stderr, "нет режима %zu %zu %zu %g; список: display_mode\n", w, h, pw, hz);
    return 1;
  }
  print_mode("выбран: ", t[i]);
  if (!want_set) return 0;

  print_mode("было:   ", cur);
  printf("откат:  display_mode set %zu %zu %zu %g\n", cur.w, cur.h, cur.pw, cur.hz);
  CGDisplayConfigRef cfg;
  CGError err = CGBeginDisplayConfiguration(&cfg);
  if (err == kCGErrorSuccess) {
    err = CGConfigureDisplayWithDisplayMode(cfg, d, refs[i], NULL);
    if (err == kCGErrorSuccess) err = CGCompleteDisplayConfiguration(cfg, kCGConfigurePermanently);
    else CGCancelDisplayConfiguration(cfg);
  }
  if (err != kCGErrorSuccess) {
    fprintf(stderr, "FAIL: CGError=%d, экран не менялся\n", err);
    return 1;
  }
  /* Режим может встать не мгновенно: перечитываем до 2 секунд. */
  struct mode now = cur;
  for (int tries = 0; tries < 20; tries++) {
    if (current(d, &now) && same(now, t[i])) break;
    usleep(100000);
  }
  print_mode("сейчас: ", now);
  if (!same(now, t[i])) {
    fprintf(stderr, "MISMATCH: встал не тот режим\n");
    return 1;
  }
  printf("OK\n");
  return 0;
}
