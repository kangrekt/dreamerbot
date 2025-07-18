import requests
import json
import time
from bs4 import BeautifulSoup
import re
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import track
from rich import print as rprint
from rich.text import Text
from rich.box import ROUNDED
from rich.align import Align
from rich.layout import Layout
from rich.prompt import Prompt, Confirm
from rich.logging import RichHandler
import logging
import random

# Setup Rich Console
console = Console()

# Setup Rich Logger
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, markup=True)]
)
log = logging.getLogger("rich")

def print_header():
    """Print header dengan gaya keren yang memenuhi lebar layar"""
    # Dapatkan lebar terminal
    width = console.width
    
    # Buat garis horizontal yang menyesuaikan lebar terminal
    horizontal_line = "═" * (width - 4)  # -4 untuk padding kiri dan kanan
    
    # Buat header dengan lebar yang menyesuaikan
    header = f"""
[bold blue]╔{horizontal_line}╗
║{'DREAMER QUESTS BOT'.center(width-2)}║
║{'BYE: KANGREKT'.center(width-2)}║
╚{horizontal_line}╝[/]
"""
    console.print(header, justify="center")

def print_success(message):
    """Print pesan sukses"""
    console.print(f"[bold green]✓ {message}[/]")

def print_error(message):
    """Print pesan error"""
    console.print(f"[bold red]✗ {message}[/]")

def print_info(message):
    """Print pesan informasi"""
    console.print(f"[bold cyan]ℹ {message}[/]")

def print_warning(message):
    """Print pesan peringatan"""
    console.print(f"[bold yellow]⚠ {message}[/]")

def print_task(task_title, points, status=""):
    """Print informasi task dengan format rapi"""
    status_icon = "✓" if status == "completed" else "•"
    status_color = "green" if status == "completed" else "yellow"
    console.print(f"[{status_color}]{status_icon}[/] [bold]{task_title}[/] - [cyan]{points} poin[/]")

def print_spin_result(prize, points, history=None):
    """Print hasil spin dengan gaya keren"""
    console.rule("[bold blue]🎡 HASIL SPIN HARIAN")
    console.print(f"🎁 [bold green]Hadiah:[/] {prize}")
    console.print(f"⭐ [bold yellow]Poin Spin:[/] {points}")
    
    if history:
        console.rule("📜 RIWAYAT SPIN")
        for item in history[-3:]:  # Tampilkan 3 riwayat terakhir
            console.print(f"📅 [bold]{item.get('date', 'N/A')}:[/] {item.get('prize', 'N/A')} - {item.get('points', 0)} poin")
    console.rule(style="blue")

def load_proxies():
    """Load proxy dari file proxies.txt"""
    try:
        with open('proxies.txt', 'r') as f:
            proxies = [line.strip() for line in f if line.strip()]
            
        if not proxies:
            print_warning("File proxies.txt kosong!")
            return []
            
        print_info(f"Berhasil memuat {len(proxies)} proxy")
        return proxies
    except FileNotFoundError:
        print_error("File proxies.txt tidak ditemukan!")
        return []
    except Exception as e:
        print_error(f"Gagal memuat proxy: {e}")
        return []

def get_random_proxy(proxies):
    """Ambil proxy secara random"""
    if not proxies:
        return None
    return random.choice(proxies)

def format_proxy_for_requests(proxy_url):
    """Format proxy untuk requests"""
    try:
        if proxy_url.startswith('http://'):
            return {
                'http': proxy_url,
                'https': proxy_url
            }
        else:
            # Jika tidak ada protocol, tambahkan http://
            formatted_proxy = f"http://{proxy_url}"
            return {
                'http': formatted_proxy,
                'https': formatted_proxy
            }
    except Exception as e:
        print_error(f"Gagal memformat proxy: {e}")
        return None

def get_session(cookie, proxy=None):
    """Mendapatkan data sesi dari API"""
    log.info("Mendapatkan data sesi...")
    url = 'https://server.partofdream.io/user/session'
    
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.5',
        'content-type': 'application/json',
        'origin': 'https://dreamerquests.partofdream.io',
        'priority': 'u=1, i',
        'referer': 'https://dreamerquests.partofdream.io/',
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Brave";v="138"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
    }
    
    cookies = {
        'connect.sid': cookie.split('=', 1)[1]
    }
    
    try:
        response = requests.post(url, headers=headers, cookies=cookies, json={}, proxies=proxy, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        log.error(f"Gagal mendapatkan data sesi: {e}")
        return None

def get_tasks(cookie, proxy=None):
    """Mendapatkan daftar task yang tersedia dari API"""
    log.info("Mengambil daftar task...")
    # Get user ID first
    session = get_session(cookie, proxy)
    if not session or 'user' not in session:
        return None
    
    user_id = session['user']['_id']
    completed_tasks = session['user'].get('completedTasks', [])
    url = f'https://server.partofdream.io/task/getTasks?id={user_id}'
    
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.5',
        'origin': 'https://dreamerquests.partofdream.io',
        'priority': 'u=1, i',
        'referer': 'https://dreamerquests.partofdream.io/',
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Brave";v="138"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
    }
    
    cookies = {
        'connect.sid': cookie.split('=', 1)[1]
    }
    
    try:
        response = requests.get(url, headers=headers, cookies=cookies, proxies=proxy, timeout=10)
        response.raise_for_status()
        tasks_data = response.json()
        
        if tasks_data and isinstance(tasks_data, dict) and 'tasks' in tasks_data:
            # Filter tasks yang belum claimed
            unclaimed_tasks = [
                task for task in tasks_data['tasks']
                if task['_id'] not in completed_tasks
            ]
            
            # Tambahkan status claimed ke setiap task
            for task in tasks_data['tasks']:
                task['claimed'] = task['_id'] in completed_tasks
            
            tasks_data['tasks'] = unclaimed_tasks
            return tasks_data
        return tasks_data
    except requests.exceptions.RequestException as e:
        log.error(f"Gagal mendapatkan daftar tugas: {e}")
        return None

def get_cooldown_time(cookie, proxy=None):
    """Mendapatkan sisa waktu cooldown dari halaman web"""
    try:
        with console.status("[bold blue]Mengecek waktu cooldown...") as status:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
            }
            
            cookies = {
                'connect.sid': cookie.split('=', 1)[1]
            }
            
            response = requests.get('https://dreamerquests.partofdream.io/', headers=headers, cookies=cookies, proxies=proxy, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Cari elemen yang berisi waktu cooldown
            time_element = soup.find('p', class_='flex items-center gap-2 text-white')
            if time_element and 'icon-[tabler--clock]' in str(time_element):
                return time_element.get_text(strip=True)
                
            return None
    except Exception as e:
        log.error(f"Gagal mendapatkan waktu tunggu: {e}")
        return None

def check_in(cookie, user_id, proxy=None):
    """Lakukan check-in harian"""
    log.info("Memproses check-in harian...")
    url = 'https://server.partofdream.io/checkin/checkin'
    
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.8',
        'content-type': 'application/json',
        'origin': 'https://dreamerquests.partofdream.io',
        'priority': 'u=1, i',
        'referer': 'https://dreamerquests.partofdream.io/',
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Brave";v="138"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
    }
    
    cookies = {
        'connect.sid': cookie.split('=', 1)[1]
    }
    
    data = {
        'userId': user_id,
        'timezoneOffset': -420
    }
    
    try:
        response = requests.post(url, headers=headers, cookies=cookies, json=data, proxies=proxy, timeout=10)
        
        # Cek status code 400 yang menandakan cooldown
        if response.status_code == 400:
            cooldown = get_cooldown_time(cookie, proxy)
            if cooldown:
                print(f"\n❌ Spin belum tersedia. Waktu tersisa: {cooldown}")
            else:
                print("\n❌ Spin belum tersedia.")
            return False
            
        response.raise_for_status()
        result = response.json()
        
        if 'message' in result:
            if 'already checked-in' in result['message'].lower():
                print_warning("\n❌ Kamu sudah melakukan check-in.")
            else:
                print_success(f"\n✅ {result['message']}")
        
        if 'user' in result:
            user_data = result['user']
            if user_data.get('checkInHistory', [{}])[0].get('usdt', 0) > 0:
                print(f"💰 USDT: {user_data.get('checkInHistory', [{}])[0].get('usdt', 0)}")
        
        return True
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None and e.response.status_code == 400:
            print_warning("❌ Kamu sudah melakukan check-in.")
        else:
            log.error(f"Gagal melakukan check-in: {e}")
        return False

def spin_daily(cookie, proxy=None):
    """Lakukan spin daily dan otomatis check-in"""
    console.clear()
    print_header()
    
    with console.status("[bold blue]Memulai prosedur spin harian...") as status:
        session = get_session(cookie, proxy)
        if not session or 'user' not in session:
            print_error("Gagal mendapatkan sesi pengguna")
            return False
    
    user_id = session['user']['_id']
    url = 'https://server.partofdream.io/spin/spin'
    
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.5',
        'content-type': 'application/json',
        'origin': 'https://dreamerquests.partofdream.io',
        'priority': 'u=1, i',
        'referer': 'https://dreamerquests.partofdream.io/',
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Brave";v="138"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
    }
    
    cookies = {
        'connect.sid': cookie.split('=', 1)[1]
    }
    
    data = {
        'userId': user_id,
        'timezoneOffset': -420
    }
    
    try:
        response = requests.post(url, headers=headers, cookies=cookies, json=data, proxies=proxy, timeout=10)
        
        # Cek status code 400 yang menandakan cooldown
        if response.status_code == 400:
            cooldown = get_cooldown_time(cookie, proxy)
            if cooldown:
                print(f"\n❌ Spin belum tersedia. Waktu tersisa: {cooldown}")
            else:
                print("\n❌ Spin belum tersedia.")
            return False
            
        response.raise_for_status()
        result = response.json()
        
        if 'message' in result:
            print(f"\n✅ {result['message']}")
        
        if 'user' in result:
            user_data = result['user']
            print("\n=== HASIL SPIN ===")
            if 'prize' in user_data:
                print(f"🎁 Hadiah: {user_data['prize']}")
            if 'spinPoints' in user_data:
                print(f"⭐ Poin Spin: {user_data['spinPoints']}")
            if 'spinUsdt' in user_data and user_data['spinUsdt'] > 0:
                print(f"💰 USDT: {user_data['spinUsdt']}")
            
            # Tampilkan riwayat spin terbaru jika ada
            if 'spinHistory' in user_data and user_data['spinHistory']:
                latest_spin = user_data['spinHistory'][0]  # Ambil yang terbaru
                print("\n=== RIWAYAT SPIN TERBARU ===")
                print(f"📅 Tanggal: {latest_spin.get('date', 'N/A')}")
                print(f"⭐ Poin: {latest_spin.get('points', 0)}")
                if latest_spin.get('usdt', 0) > 0:
                    print(f"💰 USDT: {latest_spin.get('usdt', 0)}")
        
        # Setelah spin berhasil, lakukan check-in
        console.print("\n")
        with console.status("[bold blue]Melakukan check-in harian...") as status:
            check_in_success = check_in(cookie, user_id, proxy)
        
        return check_in_success
        
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None and e.response.status_code == 400:
            print_error("Spin belum tersedia.")
            cooldown = get_cooldown_time(cookie, proxy)
            if cooldown:
                print_warning(f"Waktu tunggu tersisa: {cooldown}")
        else:
            print_error(f"Gagal melakukan spin: {e}")
        return False

def complete_task(cookie, task_id, proxy=None):
    """Menyelesaikan task dan mengklaim poin"""
    session = get_session(cookie, proxy)
    if not session or 'user' not in session:
        print_error("Gagal mendapatkan sesi pengguna")
        return False
    
    user_id = session['user']['_id']
    url = 'https://server.partofdream.io/task/completeTask/Delay'
    
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.5',
        'content-type': 'application/json',
        'origin': 'https://dreamerquests.partofdream.io',
        'priority': 'u=1, i',
        'referer': 'https://dreamerquests.partofdream.io/',
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Brave";v="138"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
    }
    
    cookies = {
        'connect.sid': cookie.split('=', 1)[1]
    }
    
    data = {
        'taskId': task_id,
        'userId': user_id
    }
    
    try:
        print("\n🔄 Mengirim permintaan penyelesaian tugas...")
        response = requests.post(url, headers=headers, cookies=cookies, json=data, proxies=proxy, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        # Tampilkan pesan dari server jika ada
        if 'message' in result:
            print(f"✅ {result['message']}")
        
        # Cari kunci yang berisi poin (bisa bervariasi)
        points = None
        point_keys = ['points', 'rewardPoints', 'pointsEarned', 'reward']
        
        for key in point_keys:
            if key in result:
                points = result[key]
                break
        
        # Jika poin tidak ditemukan langsung, cek di dalam objek reward
        if points is None and 'reward' in result and isinstance(result['reward'], dict):
            for key in point_keys:
                if key in result['reward']:
                    points = result['reward'][key]
                    break
        
        if points is not None:
            print(f"🎉 Poin yang didapat: {points}")
        else:
            print("ℹ️ Tidak ada informasi poin dalam respons")
            # Tampilkan respons lengkap untuk debugging
            print("\n📋 Respons server:", result)
        
        return True
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                print(f"\n❌ Gagal menyelesaikan tugas: {error_data.get('message', str(e))}")
            except:
                print(f"\n❌ Gagal menyelesaikan tugas: {e}")
        else:
            print(f"\n❌ Gagal menyelesaikan tugas: {e}")
        return False

def process_session(cookie, menu_choice, skip_tasks, proxy=None):
    console.print(f"\n{'='*50}")
    console.print(f"[bold]Memproses sesi...[/]")
    
    if proxy:
        print_info(f"Menggunakan proxy: {proxy['http']}")
    
    try:
        # Cek validitas cookie
        session = get_session(cookie, proxy)
        if not session or 'user' not in session:
            print_error("Gagal login! Pastikan cookie valid.")
            return False
            
        user_email = session['user'].get('email', 'Unknown')
        console.print(f"[cyan]Akun:[/] {user_email}")
        
        if menu_choice == '1':
            return process_tasks(cookie, skip_tasks, proxy)
        elif menu_choice == '2':
            return process_spin(cookie, session['user']['_id'], proxy)
            
    except Exception as e:
        print_error(f"Terjadi kesalahan: {str(e)}")
        return False

def process_tasks(cookie, skip_tasks, proxy=None):
    tasks = get_tasks(cookie, proxy)
    if not tasks or 'tasks' not in tasks or not tasks['tasks']:
        print_error("Tidak ada tugas yang tersedia untuk saat ini.")
        return False
        
    console.print("\n[bold]Daftar Tugas yang Tersedia:[/]")
    task_list = []
    displayed_count = 0
    
    for task in tasks['tasks']:
        # Skip task yang ada di skip_tasks atau terkait email/wallet
        if (task['title'] in skip_tasks or 
            'connect your email' in task['title'].lower() or 
            'connect your wallet' in task['title'].lower()):
            continue
            
        displayed_count += 1
        console.print(f"{displayed_count}. {task['title']} - {task.get('points', 0)} poin")
        task_list.append(task)
    
    if not task_list:
        print_error("Tidak ada tugas yang tersedia untuk diselesaikan.")
        return False
        
    # Langsung menyelesaikan semua task tanpa konfirmasi
    success_count = 0
    with console.status("[bold blue]Menyelesaikan task...[/]"):
        for task in task_list:
            try:
                console.print(f"\n[bold]Menyelesaikan:[/] {task['title']}")
                if complete_task(cookie, task['_id'], proxy):
                    print_success(f"Berhasil: {task['title']}")
                    success_count += 1
                else:
                    print_error(f"Gagal: {task['title']}")
            except Exception as e:
                print_error(f"Error: {str(e)}")
    
    console.print(f"\n[bold green]Selesai![/] {success_count} dari {len(task_list)} task berhasil diselesaikan.")
    return True

def process_spin(cookie, user_id, proxy=None):
    console.print("\n[bold]Memproses spin harian...[/]")
    spin_success = spin_daily(cookie, proxy)
    
    if not spin_success:
        console.print("\n[bold]Mencoba check-in harian...[/]")
        check_in(cookie, user_id, proxy)
    
    return True

def main():
    # Daftar task yang akan di-skip (tidak perlu diklaim)
    skip_tasks = [
        'Follow us on X (Twitter)',
        'Like and Retweet our post on X (Twitter)',
        'Join our Discord Server',
        'Subscribe to our YouTube channel',
        'Follow us on Instagram',
        'Join our Telegram channel',
        'Join our Telegram group',
        'Join our Discord server',
        'Follow us on X',
        'Like and Retweet our post on X',
    ]
    
    # Tampilkan header
    print_header()
    
    try:
        # Baca semua cookie dari file
        with open('cookies.txt', 'r') as f:
            cookies = [line.strip() for line in f if line.strip()]
            
        if not cookies:
            print_error("File cookies.txt kosong!")
            return
            
        while True:
            # Tampilkan menu
            console.rule("📋 MENU UTAMA", style="blue")
            menu_table = Table(show_header=False, box=ROUNDED, style="blue")
            menu_table.add_column("Pilihan", style="cyan", width=5)
            menu_table.add_column("Menu")
            
            menu_table.add_row("1️⃣", "Selesaikan Task")
            menu_table.add_row("2️⃣", "Spin Harian")
            menu_table.add_row("3️⃣", "Keluar")
            
            console.print(menu_table)
            
            choice = Prompt.ask(
                "\n[bold cyan]Pilih menu[/]",
                choices=['1', '2', '3']
            )
            
            if choice in ['1', '2']:
                # Tanyakan apakah ingin menggunakan proxy
                use_proxy = Prompt.ask(
                    "\n[bold yellow]Gunakan Proxy?[/]",
                    choices=['y', 'n'],
                    default='n'
                )
                
                proxies = []
                if use_proxy.lower() == 'y':
                    proxies = load_proxies()
                    if not proxies:
                        print_warning("Tidak ada proxy yang tersedia, melanjutkan tanpa proxy.")
                
                # Proses semua sesi satu per satu
                for i, cookie in enumerate(cookies, 1):
                    console.print(f"\n[bold]Sesi {i} dari {len(cookies)}[/]")
                    
                    # Pilih proxy random jika tersedia
                    proxy = None
                    if proxies:
                        proxy_url = get_random_proxy(proxies)
                        proxy = format_proxy_for_requests(proxy_url)
                        if not proxy:
                            print_warning("Gagal memformat proxy, melanjutkan tanpa proxy.")
                    
                    process_session(cookie, choice, skip_tasks, proxy)
                    
                    # Jeda antar sesi
                    if i < len(cookies):
                        console.print("\n[dim]Menyiapkan sesi berikutnya...[/]")
                        time.sleep(2)
                
                console.print("\n[bold green]Semua sesi telah diproses![/]")
                
                # Jika memilih menu 2 (Spin Harian), tambahkan looping otomatis
                if choice == '2':
                    # Tunggu 24 jam + 2 menit
                    wait_time = 24 * 60 * 60 + 2 * 60  # 24 jam + 2 menit
                    console.print("\n[bold]Memulai countdown untuk spin berikutnya...[/]")
                    
                    # Tampilkan waktu sisa dalam format jam:menit:detik
                    with console.status("[bold blue]Menunggu waktu berikutnya...[/]") as status:
                        while wait_time > 0:
                            hours = wait_time // 3600
                            minutes = (wait_time % 3600) // 60
                            seconds = wait_time % 60
                            status.update(f"[bold]Waktu tersisa: {hours:02d}:{minutes:02d}:{seconds:02d}[/]")
                            time.sleep(1)
                            wait_time -= 1
                    
                    console.print("\n[bold green]Waktu telah berakhir! Memulai spin harian baru...[/]")
                    continue
                
            elif choice == '3':
                console.print("\n[dim]Tekan Enter untuk keluar...[/]")
                input()
                break
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Bot dihentikan oleh pengguna.[/]")
        return
    except Exception as e:
        print_error(f"Terjadi kesalahan: {str(e)}")
        return
    finally:
        console.print("\n[dim]Tekan Enter untuk keluar...[/]")
        input()

if __name__ == "__main__":
    import time
    main()