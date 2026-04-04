import pygame
import random

LARGURA_JOGO = 1280
ALTURA_JOGO = 1024

pygame.init()
clock = pygame.time.Clock()
info = pygame.display.Info()
janela = pygame.display.set_mode((LARGURA_JOGO, ALTURA_JOGO), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption('Dark Void: Stellar Rebellion')

tela_cheia = True

def carregar_assets():
    assets = {
        'fundo': pygame.image.load('assets/Fundo_ceu_noite.png').convert(),
        'jogador': pygame.image.load('assets/jogadoor.png').convert_alpha(),
        'inimigo': pygame.image.load('assets/inimigoo.png').convert_alpha(),
        'chefe': pygame.image.load('assets/boss_final.png').convert_alpha(),
        'laser_jogador': pygame.image.load('assets/laser_jogador.png').convert_alpha(),
        'laser_inimigo': pygame.image.load('assets/laser_inimigo.png').convert_alpha(),
        'explosao': pygame.image.load('assets/explosao.png').convert_alpha(),
        'som_tiro': pygame.mixer.Sound('assets/laser.wav'),
        'som_explosao': pygame.mixer.Sound('assets/explosao.wav')
    }
    return assets

def configurar_jogo():
    return {
        'volume': 0.3,
        'pontuacao': 0,
        'vidas': 15,
        'fase': 1,
        'max_fases': 6,
        'pausado': False,
        'fim_de_jogo': False,
        'vitoria': False
    }

def configurar_jogador():
    return {
        'x': 530,
        'y': 760,
        'velocidade': 8,
        'invulneravel': False,
        'tempo_invulneravel': 0,
        'duracao_invulnerabilidade': 90
    }

def configurar_boss():
    return {
        'ativo': False,
        'vida': 20,
        'x': 600,
        'y': 120,
        'warning': False,
        'tempo_warning': 0
    }

def criar_inimigos():
    inimigos = []
    for linha in range(4):
        for coluna in range(6):
            x = 150 + coluna * 150
            y = 80 + linha * 100
            inimigos.append([x, y])
    return inimigos

def ajustar_volume(assets, delta):
    jogo['volume'] = max(0.0, min(1.0, jogo['volume'] + delta))
    assets['som_tiro'].set_volume(jogo['volume'])
    assets['som_explosao'].set_volume(jogo['volume'])

def mover_jogador(teclas, jogador):
    if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
        jogador['x'] -= jogador['velocidade']
    if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
        jogador['x'] += jogador['velocidade']
    if teclas[pygame.K_UP] or teclas[pygame.K_w]:
        jogador['y'] -= jogador['velocidade']
    if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
        jogador['y'] += jogador['velocidade']

    jogador['x'] = max(0, min(jogador['x'], 1180))
    jogador['y'] = max(4, min(jogador['y'], 900))

def atirar(teclas, tiro, jogador, assets):
    if teclas[pygame.K_SPACE] and not tiro['ativo']:
        tiro['ativo'] = True
        assets['som_tiro'].play()
        tiro['x'] = jogador['x'] + 40
        tiro['y'] = jogador['y']

def mover_tiro_jogador(tiro):
    if tiro['ativo']:
        tiro['y'] -= 12
        if tiro['y'] < 0:
            tiro['ativo'] = False

def mover_inimigos(inimigos, direcao, velocidade):
    trocar_direcao = False
    for inimigo in inimigos:
        inimigo[0] += velocidade * direcao
        if inimigo[0] <= 0 or inimigo[0] >= 1180:
            trocar_direcao = True

    if trocar_direcao:
        direcao *= -1
        pode_descer = all(inimigo[1] + 40 <= 450 for inimigo in inimigos)
        if pode_descer:
            for inimigo in inimigos:
                inimigo[1] += 40
    return direcao

def inimigos_atirarem(inimigos, tiros_inimigos, assets):
    if inimigos and random.randint(0, 100) < 2:
        inimigo = random.choice(inimigos)
        assets['som_tiro'].play()
        tiros_inimigos.append([inimigo[0] + 40, inimigo[1] + 40])

def mover_tiros_inimigos(tiros_inimigos, jogador, jogo, jogador_state):
    for tiro in tiros_inimigos[:]:
        tiro[1] += 6
        tiro_rect = pygame.Rect(tiro[0], tiro[1], 10, 30)
        jogador_rect = pygame.Rect(jogador['x'], jogador['y'], 80, 80)

        if tiro_rect.colliderect(jogador_rect):
            tiros_inimigos.remove(tiro)
            if not jogador_state['invulneravel']:
                jogo['vidas'] -= 1
                ativar_invulnerabilidade(jogador_state)
        elif tiro[1] > 1024:
            tiros_inimigos.remove(tiro)

def ativar_invulnerabilidade(jogador_state):
    jogador_state['invulneravel'] = True
    jogador_state['tempo_invulneravel'] = jogador_state['duracao_invulnerabilidade']

def atualizar_invulnerabilidade(jogador_state):
    if jogador_state['invulneravel']:
        jogador_state['tempo_invulneravel'] -= 1
        if jogador_state['tempo_invulneravel'] <= 0:
            jogador_state['invulneravel'] = False

def verificar_colisao_jogador_inimigos(inimigos, jogador, jogo, jogador_state):
    jogador_rect = pygame.Rect(jogador['x'], jogador['y'], 80, 80)

    for inimigo in inimigos[:]:
        inimigo_rect = pygame.Rect(inimigo[0], inimigo[1], 80, 80)
        if jogador_rect.colliderect(inimigo_rect) and not jogador_state['invulneravel']:
            jogo['vidas'] -= 1
            ativar_invulnerabilidade(jogador_state)
            if jogo['vidas'] <= 0:
                jogo['fim_de_jogo'] = True
            break

def verificar_colisao_tiro_inimigos(tiro, inimigos, explosoes, assets, jogo):
    if not tiro['ativo']:
        return

    tiro_rect = pygame.Rect(tiro['x'], tiro['y'], 10, 30)

    for inimigo in inimigos[:]:
        inimigo_rect = pygame.Rect(inimigo[0], inimigo[1], 80, 80)
        if tiro_rect.colliderect(inimigo_rect):
            inimigos.remove(inimigo)
            explosoes.append([inimigo[0], inimigo[1], 20])
            assets['som_explosao'].play()
            tiro['ativo'] = False
            jogo['pontuacao'] += 3
            break

def atualizar_boss(boss, jogador, jogo, jogador_state, tiro, explosoes, tiros_inimigos, assets, direcao):
    if not boss['ativo']:
        return direcao

    jogador_rect = pygame.Rect(jogador['x'], jogador['y'], 80, 80)
    boss_rect = pygame.Rect(boss['x'], boss['y'], 200, 200)
    tiro_rect = pygame.Rect(tiro['x'], tiro['y'], 10, 30)

    if jogador_rect.colliderect(boss_rect) and not jogador_state['invulneravel']:
        jogo['vidas'] -= 3
        jogador['x'], jogador['y'] = 530, 760
        ativar_invulnerabilidade(jogador_state)
        if jogo['vidas'] <= 0:
            jogo['fim_de_jogo'] = True

    if tiro['ativo'] and tiro_rect.colliderect(boss_rect):
        boss['vida'] -= 1
        tiro['ativo'] = False
        assets['som_explosao'].play()
        if boss['vida'] <= 0:
            boss['ativo'] = False
            jogo['vitoria'] = True
            explosoes.append([boss['x'], boss['y'], 100])

    if random.randint(0, 100) < 7:
        assets['som_tiro'].play()
        tiros_inimigos.append([boss['x'] + 100, boss['y'] + 150])

    boss['x'] += 6 * direcao
    if boss['x'] <= 0 or boss['x'] >= 1080:
        direcao *= -1

    return direcao

def avancar_fase(jogo, inimigos, boss, velocidade_inimigos, velocidade_laser):
    if len(inimigos) == 0 and not boss['ativo'] and jogo['fase'] < jogo['max_fases']:
        jogo['fase'] += 1

        if jogo['fase'] == jogo['max_fases']:
            boss['warning'] = True
            boss['tempo_warning'] = 180
            boss['vida'] = 20
            boss['x'], boss['y'] = 600, 120
        else:
            velocidade_inimigos += 1
            velocidade_laser += 1

            for linha in range(4):
                for coluna in range(6):
                    x = 150 + coluna * 150
                    y = 80 + linha * 100
                    inimigos.append([x, y])

    return velocidade_inimigos, velocidade_laser

def renderizar_fundo(assets):
    janela.blit(assets['fundo'], (0, 0))

def renderizar_jogador(assets, jogador, jogador_state):
    if not (jogador_state['invulneravel'] and jogador_state['tempo_invulneravel'] % 10 < 5):
        janela.blit(assets['jogador'], (jogador['x'], jogador['y']))

def renderizar_inimigos(assets, inimigos):
    for inimigo in inimigos:
        janela.blit(assets['inimigo'], (inimigo[0], inimigo[1]))

def renderizar_tiro_jogador(assets, tiro):
    if tiro['ativo']:
        janela.blit(assets['laser_jogador'], (tiro['x'], tiro['y']))

def renderizar_tiros_inimigos(assets, tiros_inimigos):
    for tiro in tiros_inimigos:
        janela.blit(assets['laser_inimigo'], (tiro[0], tiro[1]))

def renderizar_explosoes(assets, explosoes):
    for explosao in explosoes[:]:
        janela.blit(assets['explosao'], (explosao[0], explosao[1]))
        explosao[2] -= 1
        if explosao[2] <= 0:
            explosoes.remove(explosao)

def renderizar_boss(assets, boss):
    if boss['ativo']:
        janela.blit(assets['chefe'], (boss['x'], boss['y']))

def renderizar_hud(jogo, jogador_state, boss):
    fonte = pygame.font.SysFont(None, 40)

    texto_pontos = fonte.render(f'Pontos: {jogo["pontuacao"]}', True, (255, 255, 255))
    janela.blit(texto_pontos, (20, 20))

    texto_vidas = fonte.render(f'Vidas: {jogo["vidas"]}', True, (255, 255, 255))
    janela.blit(texto_vidas, (20, 60))

    texto_fase = fonte.render(f'Fase: {jogo["fase"]}/{jogo["max_fases"]}', True, (255, 255, 255))
    janela.blit(texto_fase, (20, 100))

    if jogador_state['invulneravel']:
        texto_inv = fonte.render('INVULNERÁVEL', True, (0, 255, 255))
        janela.blit(texto_inv, (20, 140))

    if boss['ativo']:
        texto_boss = fonte.render(f'Boss HP: {boss["vida"]}', True, (255, 50, 50))
        janela.blit(texto_boss, (1000, 20))

def renderizar_tela_warning(boss, assets):
    janela.blit(assets['fundo'], (0, 0))
    fonte_grande = pygame.font.SysFont(None, 120)

    texto_warning = fonte_grande.render("⚠ AVISO!! ⚠", True, (255, 0, 0))
    texto_boss = fonte_grande.render("BOSS", True, (255, 255, 255))

    janela.blit(texto_warning, (380, 400))
    janela.blit(texto_boss, (330, 520))

    boss['tempo_warning'] -= 1
    if boss['tempo_warning'] <= 0:
        boss['warning'] = False
        boss['ativo'] = True

def renderizar_tela_pausa(jogo):
    janela.blit(assets['fundo'], (0, 0))
    fonte_grande = pygame.font.SysFont(None, 80)
    fonte_media = pygame.font.SysFont(None, 40)

    texto_pause = fonte_grande.render("PAUSADO", True, (255, 255, 255))
    texto_volume = fonte_media.render("Volume: + / -", True, (255, 255, 255))
    texto_continuar = fonte_media.render("Pressione P para continuar", True, (255, 255, 255))

    janela.blit(texto_pause, (500, 400))
    janela.blit(texto_volume, (500, 500))
    janela.blit(texto_continuar, (450, 550))

def renderizar_tela_vitoria(jogo):
    janela.blit(assets['fundo'], (0, 0))
    fonte_grande = pygame.font.SysFont(None, 100)
    fonte_media = pygame.font.SysFont(None, 50)

    texto_vitoria = fonte_grande.render("PARABÉNS!", True, (255, 255, 0))
    texto_vitoria2 = fonte_media.render("VOCÊ DERROTOU O BOSS", True, (255, 255, 255))
    texto_reiniciar = fonte_media.render("Pressione R para jogar novamente", True, (255, 255, 255))

    janela.blit(texto_vitoria, (460, 380))
    janela.blit(texto_vitoria2, (420, 460))
    janela.blit(texto_reiniciar, (380, 540))

def renderizar_tela_gameover():
    janela.blit(assets['fundo'], (0, 0))
    fonte_grande = pygame.font.SysFont(None, 100)
    fonte_media = pygame.font.SysFont(None, 50)

    texto_gameover = fonte_grande.render("FIM DE JOGO", True, (255, 0, 0))
    texto_reiniciar = fonte_media.render("Pressione R para reiniciar", True, (255, 255, 255))

    janela.blit(texto_gameover, (420, 400))
    janela.blit(texto_reiniciar, (400, 500))

def reiniciar_jogo():
    global jogo, jogador, inimigos, tiros_inimigos, tiro
    global explosoes, direcao_inimigos, velocidade_inimigos, velocidade_laser_inimigo, boss

    jogo = configurar_jogo()
    jogador = configurar_jogador()
    boss = configurar_boss()
    inimigos = criar_inimigos()
    tiros_inimigos = []
    explosoes = []
    direcao_inimigos = 1
    velocidade_inimigos = 2
    velocidade_laser_inimigo = 6

    tiro = {'ativo': False, 'x': 0, 'y': 0}

assets = carregar_assets()
jogo = configurar_jogo()
jogador = configurar_jogador()
boss = configurar_boss()
inimigos = criar_inimigos()
tiros_inimigos = []
explosoes = []
direcao_inimigos = 1
velocidade_inimigos = 2
velocidade_laser_inimigo = 6
tiro = {'ativo': False, 'x': 0, 'y': 0}

assets['som_tiro'].set_volume(jogo['volume'])
assets['som_explosao'].set_volume(jogo['volume'])

loop = True
while loop:

    for events in pygame.event.get():
        if events.type == pygame.QUIT:
            loop = False

        if events.type == pygame.KEYDOWN:
            if events.key == pygame.K_F11:
                tela_cheia = not tela_cheia

                pygame.display.quit()
                pygame.display.init()

                if tela_cheia:
                    janela = pygame.display.set_mode((LARGURA_JOGO, ALTURA_JOGO), pygame.FULLSCREEN | pygame.SCALED)
                else:
                    janela = pygame.display.set_mode((LARGURA_JOGO, ALTURA_JOGO))

        if events.type == pygame.KEYDOWN:
            if events.key == pygame.K_p:
                jogo['pausado'] = not jogo['pausado']
            if events.key == pygame.K_EQUALS or events.key == pygame.K_PLUS:
                ajustar_volume(assets, 0.1)
            if events.key == pygame.K_MINUS:
                ajustar_volume(assets, -0.1)

    teclas = pygame.key.get_pressed()

    if boss['warning']:
        renderizar_tela_warning(boss, assets)
        pygame.display.update()
        clock.tick(60)
        continue

    if jogo['pausado']:
        renderizar_tela_pausa(jogo)
        pygame.display.update()
        clock.tick(60)
        continue

    if jogo['vitoria']:
        renderizar_tela_vitoria(jogo)
        if teclas[pygame.K_r]:
            reiniciar_jogo()
        pygame.display.update()
        clock.tick(60)
        continue

    if jogo['fim_de_jogo']:
        renderizar_tela_gameover()
        if teclas[pygame.K_r]:
            reiniciar_jogo()
        pygame.display.update()
        clock.tick(60)
        continue

    atualizar_invulnerabilidade(jogador)
    mover_jogador(teclas, jogador)
    atirar(teclas, tiro, jogador, assets)
    mover_tiro_jogador(tiro)

    direcao_inimigos = mover_inimigos(inimigos, direcao_inimigos, velocidade_inimigos)
    inimigos_atirarem(inimigos, tiros_inimigos, assets)
    mover_tiros_inimigos(tiros_inimigos, jogador, jogo, jogador)

    verificar_colisao_jogador_inimigos(inimigos, jogador, jogo, jogador)
    verificar_colisao_tiro_inimigos(tiro, inimigos, explosoes, assets, jogo)

    direcao_inimigos = atualizar_boss(boss, jogador, jogo, jogador, tiro, explosoes, tiros_inimigos, assets,
                                      direcao_inimigos)

    velocidade_inimigos, velocidade_laser_inimigo = avancar_fase(jogo, inimigos, boss, velocidade_inimigos,
                                                                 velocidade_laser_inimigo)

    renderizar_fundo(assets)
    renderizar_inimigos(assets, inimigos)
    renderizar_jogador(assets, jogador, jogador)
    renderizar_tiro_jogador(assets, tiro)
    renderizar_tiros_inimigos(assets, tiros_inimigos)
    renderizar_explosoes(assets, explosoes)
    renderizar_boss(assets, boss)
    renderizar_hud(jogo, jogador, boss)

    pygame.display.update()
    clock.tick(60)

pygame.quit()