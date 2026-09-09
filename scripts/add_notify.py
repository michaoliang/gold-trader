path = r"E:\MySoftware\黄金分析工具_Portable\黄金分析助手.py"
content = open(path, encoding="utf-8").read()

# 1. Add imports for winsound and win10toast
old_imports = '''try:
    import matplotlib
    matplotlib.use('TkAgg')
    matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
    matplotlib.rcParams['axes.unicode_minus'] = False
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    from matplotlib.patches import Rectangle
except ImportError:
    print("matplotlib not found"); exit(1)'''

new_imports = '''try:
    import matplotlib
    matplotlib.use('TkAgg')
    matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
    matplotlib.rcParams['axes.unicode_minus'] = False
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    from matplotlib.patches import Rectangle
except ImportError:
    print("matplotlib not found"); exit(1)

try:
    import winsound
    HAS_SOUND = True
except ImportError:
    HAS_SOUND = False

try:
    from win10toast import ToastNotifier
    HAS_TOAST = True
except ImportError:
    HAS_TOAST = False'''

if old_imports in content and new_imports not in content:
    content = content.replace(old_imports, new_imports)
    print("Added imports for winsound and win10toast")
else:
    print("Imports already present or pattern not found")

open(path, "w", encoding="utf-8").write(content)
