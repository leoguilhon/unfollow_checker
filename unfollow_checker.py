import tkinter as tk
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
from threading import Thread
from webdriver_manager.chrome import ChromeDriverManager
import os
import shutil

# Variável global para armazenar o total de pessoas que não te seguem de volta
total_not_followed_back = 0

# Função para fazer login no Instagram
def login_instagram(username, password):
    while True:
        # Inicializa o navegador
        chrome_driver_path = "C:/ChromeDriver/chromedriver.exe"
        # Configura as opções do ChromeDriver se necessário
        chrome_options = webdriver.ChromeOptions()
        # Por exemplo, adicionar opções para desabilitar as notificações
        chrome_options.add_argument("--disable-notifications")
        
        # Inicializa o navegador
        driver = webdriver.Chrome(executable_path=chrome_driver_path, options=chrome_options)
        driver.get("https://www.instagram.com")

        # Espera um pouco para garantir que a página seja carregada
        time.sleep(2)

        # Encontra os campos de username e password e preenche com as informações fornecidas
        driver.find_element(By.NAME, "username").send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)

        # Encontra o botão de login e clica nele
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Espera o login ser feito
        time.sleep(5)

        # Verifica se a página foi redirecionada para a página de login novamente, o que indica credenciais inválidas
        try:
            # Verifica se o campo de input de username ainda está preenchido, indicando falha no login
            username_input = driver.find_element(By.NAME, "username")
            if username_input.get_attribute("value"):
                print("Nome de usuário ou senha inválido.")
                driver.quit()
                break
            else:
                return driver
        except NoSuchElementException:
            try:
            # Verifica se há um campo de verificação de código após o login
                verification_code_input = driver.find_element(By.NAME, "verificationCode")
                print("Verificação de duas etapas necessária. Aguardando a inserção do código de verificação...")
                while verification_code_input.is_displayed():
                    time.sleep(2)
                    # Atualiza o elemento para evitar o StaleElementReferenceException
                    verification_code_input = driver.find_element(By.NAME, "verificationCode")
                print("Código de verificação inserido. Continuando o login...")
            except NoSuchElementException:
                pass
            return driver

# Função para obter os seguidores
def get_followers(driver, username):
    driver.get("https://www.instagram.com/" + username)

    # Espera um pouco para garantir que a página seja carregada
    time.sleep(2)

    # Verifica se o botão de seguidores está presente e clicável
    try:
        followers_button = driver.find_element(By.CSS_SELECTOR, "a[href*='/followers/']")
        if followers_button.is_enabled():
            followers_button.click()
            # Espera um pouco mais para garantir que a lista de seguidores seja carregada
            time.sleep(5)

            # Rola o diálogo dos seguidores até o final
            while True:
                # Encontra o último seguidor na lista atual
                last_follower = driver.find_element(By.XPATH, "(//div[@role='dialog']//a)[last()]")
                # Rola a página para que o último seguidor fique visível
                driver.execute_script("arguments[0].scrollIntoView();", last_follower)
                time.sleep(2)
                # Verifica se o último seguidor ainda está visível na tela
                if last_follower.location_once_scrolled_into_view['y'] < driver.execute_script("return window.innerHeight"):
                    break
                # Clica no último seguidor para carregar mais seguidores
                last_follower.click()
                time.sleep(5)

            # Verifica se ainda há mais seguidores para carregar
            while True:
                # Encontra o último seguidor na lista atual
                last_follower = driver.find_element(By.XPATH, "(//div[@role='dialog']//a)[last()]")
                # Rola a página para que o último seguidor fique visível
                driver.execute_script("arguments[0].scrollIntoView();", last_follower)
                time.sleep(2)
                # Verifica se o último seguidor mudou
                new_last_follower = driver.find_element(By.XPATH, "(//div[@role='dialog']//a)[last()]")
                if new_last_follower != last_follower:
                    last_follower = new_last_follower
                else:
                    break

            # Encontra os elementos âncora que representam os nomes dos seguidores
            followers_elems = driver.find_elements(By.CSS_SELECTOR, "div[role='dialog'] div a[href*='/'] span")

            # Obtém os nomes dos seguidores
            followers = [elem.text for elem in followers_elems]

            return followers
        else:
            messagebox.showerror("Erro", "O botão de seguidores não está clicável.")
            return []
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro ao obter os seguidores: {e}")
        return []

# Função para obter quem você segue
def get_followings(driver, username):
    driver.get("https://www.instagram.com/" + username)

    # Espera um pouco para garantir que a página seja carregada
    time.sleep(2)

    # Encontra o botão de usuários que segue
    following_button = driver.find_element(By.CSS_SELECTOR, "a[href*='/following/']")
    following_button.click()
    # Espera um pouco mais para garantir que a lista de usuários que segue seja carregada
    time.sleep(5)

    # Rola o diálogo dos usuários que segue até o final
    while True:
        # Encontra o último usuário que segue na lista atual
        last_following = driver.find_element(By.XPATH, "(//div[@role='dialog']//a)[last()]")
        # Rola a página para que o último usuário que segue fique visível
        driver.execute_script("arguments[0].scrollIntoView();", last_following)
        time.sleep(2)
        # Verifica se o último usuário que segue ainda está visível na tela
        if last_following.location_once_scrolled_into_view['y'] < driver.execute_script("return window.innerHeight"):
            break
        # Clica no último usuário que segue para carregar mais usuários
        last_following.click()
        time.sleep(5)

    # Verifica se ainda há mais usuários que segue para carregar
    while True:
        # Encontra o último usuário que segue na lista atual
        last_following = driver.find_element(By.XPATH, "(//div[@role='dialog']//a)[last()]")
        # Rola a página para que o último usuário que segue fique visível
        driver.execute_script("arguments[0].scrollIntoView();", last_following)
        time.sleep(2)
        # Verifica se o último usuário que segue mudou
        new_last_following = driver.find_element(By.XPATH, "(//div[@role='dialog']//a)[last()]")
        if new_last_following != last_following:
            last_following = new_last_following
        else:
            break

    # Encontra os elementos âncora que representam os nomes dos usuários que segue
    following_elems = driver.find_elements(By.CSS_SELECTOR, "div[role='dialog'] div a[href*='/'] span")

    # Obtém os nomes dos usuários que segue
    following = [elem.text for elem in following_elems]

    return following

# Função para verificar quem não te segue de volta
def check_not_followed_back(username, password):
    # Exibe a janela de espera
    wait_window = show_wait_window()

    # Realiza o login no Instagram
    driver = login_instagram(username, password)

    if driver:
        print('Isso pode demorar alguns minutos. Por favor, aguarde ate que o processo seja concluido...\n')
        # Obtém os seguidores
        followers = get_followers(driver, username)

        # Obtém quem você segue
        followings = get_followings(driver, username)

        # Fecha o navegador
        driver.quit()

        if followers and followings:
            # Identifica quem não te segue de volta
            not_followed_back = [following for following in followings if following not in followers]
            global total_not_followed_back
            total_not_followed_back = len(not_followed_back)

            # Exibe os usuários que não te seguem de volta em páginas
            display_paged_results(not_followed_back)
        else:
            messagebox.showerror("Erro", "Não foi possível obter a lista de seguidores ou de seguidos.")
    else:
        messagebox.showerror("Erro", "Não foi possível fazer login no Instagram.")

    # Destroi a janela de espera
    destroy_wait_window(wait_window)

# Função para exibir uma janela de espera
def show_wait_window():
    wait_window = tk.Toplevel()
    wait_window.title("Aguarde...")
    wait_window.attributes('-topmost', True)  # Mantém a janela sempre na frente
    wait_window.geometry("250x30+{}+{}".format(
        (wait_window.winfo_screenwidth() - 200) // 2,
        (wait_window.winfo_screenheight() - 100) // 2))  # Ajuste de tamanho
    wait_label = tk.Label(wait_window, text="Por favor, aguarde...")
    wait_label.pack()
    return wait_window

# Função para destruir a janela de espera
def destroy_wait_window(wait_window):
    wait_window.destroy()

# Função para exibir os resultados em páginas
def display_paged_results(results):
    num_results = len(results)
    page_size = 15
    num_pages = (num_results + page_size - 1) // page_size

    current_page = 0

    def show_results(page):
        nonlocal current_page
        current_page = page
        start_index = page * page_size
        end_index = min(start_index + page_size, num_results)

        result_text.delete(1.0, tk.END)
        for user in results[start_index:end_index]:
            result_text.insert(tk.END, f"{user}\n")

        page_label.config(text=f"Página {current_page + 1} de {num_pages}")
        total_label.config(text=f"Total: {total_not_followed_back}")

    def previous_page():
        if current_page > 0:
            show_results(current_page - 1)

    def next_page():
        if current_page < num_pages - 1:
            show_results(current_page + 1)

    try:
        # Cria a janela para exibir os resultados
        result_window = tk.Toplevel()
        result_window.title("Usuários que não te seguem de volta")
        result_window.attributes('-topmost', True)  # Mantém a janela sempre na frente

        result_text = tk.Text(result_window, height=15, width=40)
        result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        page_label = tk.Label(result_window, text="", pady=5)
        page_label.pack()

        total_label = tk.Label(result_window, text="", pady=5)
        total_label.pack()

        # Mostra a primeira página de resultados
        show_results(0)

        # Adiciona botões para navegar entre as páginas
        nav_frame = tk.Frame(result_window)
        nav_frame.pack(pady=5)

        prev_button = tk.Button(nav_frame, text="Anterior", command=previous_page)
        prev_button.grid(row=0, column=0, padx=5)

        next_button = tk.Button(nav_frame, text="Próximo", command=next_page)
        next_button.grid(row=0, column=1, padx=5)

        print('Concluído!')
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro ao exibir os resultados: {e}")

# Função para exibir os sobre
def exibir_sobre():
    sobre = """
    Para o funcionamento do software, o Google Chrome
    deve estar atualizado.
    
    Desenvolvido por Leonardo Guilhon
    
    """
    # Cria uma caixa de diálogo para exibir os requisitos
    messagebox.showinfo("Sobre", sobre)
    # Chama a função para criar a interface gráfica
    create_gui()

# Função para criar a interface gráfica
def create_gui():
    # Cria a janela principal
    root = tk.Tk()
    root.title("Unfollow Checker")

    # Define o tamanho da janela
    window_width = 280
    window_height = 100
    
    # Obtém as dimensões da tela
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Calcula a posição da janela para centralizá-la na tela
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2
    
    # Define a geometria da janela para centralizá-la
    root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")


    # Chama o método lift() para garantir que a janela fique na frente
    root.lift()
    
    # Restaura o foco da janela
    root.focus_force()

    # Função para coletar os dados do usuário e chamar a função de verificação
    def verify_not_followed_back():
        username = username_entry.get()
        password = password_entry.get()

        if username and password:
            # Executa a verificação em uma thread separada para não bloquear a interface
            Thread(target=check_not_followed_back, args=(username, password)).start()
        else:
            messagebox.showerror("Erro", "Por favor, preencha o nome de usuário e senha.")

    # Label e Entry para inserir o nome de usuário
    username_label = tk.Label(root, text="Nome de Usuário:")
    username_label.grid(row=0, column=0, padx=5, pady=5)
    username_entry = tk.Entry(root)
    username_entry.grid(row=0, column=1, padx=5, pady=5)

    # Label e Entry para inserir a senha
    password_label = tk.Label(root, text="Senha:")
    password_label.grid(row=1, column=0, padx=5, pady=5)
    password_entry = tk.Entry(root, show="*")
    password_entry.grid(row=1, column=1, padx=5, pady=5)

    # Botão para iniciar a verificação
    verify_button = tk.Button(root, text="Verificar", command=verify_not_followed_back)
    verify_button.grid(row=2, column=0, columnspan=4, padx=5, pady=5)

    # Executa o loop da interface gráfica
    root.mainloop()


chrome_driver_path = ChromeDriverManager().install()
print("ChromeDriver atualizado em:", chrome_driver_path)

destination_directory = "C:\\ChromeDriver\\"
if not os.path.exists(destination_directory):
    os.makedirs(destination_directory)

# Copia o arquivo ChromeDriver para o diretório de destino
shutil.copy(chrome_driver_path, os.path.join(destination_directory, "chromedriver.exe"))

print("ChromeDriver copiado para:", destination_directory)

print('Para o funcionamento do Unfollow Checker, o seu Chrome deve estar na versao mais atual.\nCaso ocorra algum erro, verifique se o Chrome esta atualizado ou entre em contato com o desenvolvedor.\n')

# Exibe o Sobre
exibir_sobre()