import pygame
import random

pygame.init()

clock = pygame.time.Clock()

janela = pygame.display.set_mode((1280, 1024))
pygame.display.set_caption('Dark Void: Stellar Rebellion')

# assets
imagem_fundo = pygame.image.load('assets/Fundo_ceu_noite.png').convert()
nave_jogador = pygame.image.load('assets/jogadoor.png').convert_alpha()
nave_inimigo = pygame.image.load('assets/inimigoo.png').convert_alpha()
nave_inimigo_chefe = pygame.image.load('assets/boss_final.png').convert_alpha()
lazer_jogador = pygame.image.load('assets/laser_jogador.png').convert_alpha()
lazer_inimigo = pygame.image.load('assets/laser_inimigo.png').convert_alpha()
imagem_explosao = pygame.image.load('assets/explosao.png').convert_alpha()
som_tiro = pygame.mixer.Sound('assets/laser.wav')
som_explosao = pygame.mixer.Sound('assets/explosao.wav')

# volume inicial
volume = 0.3
som_tiro.set_volume(volume)
som_explosao.set_volume(volume)

# jogador
posicao_x_jogador = 530
posicao_y_jogador = 760
velocidade_jogador = 8

# INVULNERABILIDADE
invulneravel = False
tempo_invulneravel = 0
duracao_invulnerabilidade = 90  # 1.5 segundos a 60 FPS

# pontuação e vidas
pontuacao = 0
vidas = 15
fonte = pygame.font.SysFont(None, 40)

# fases
fase = 1
max_fases = 6

# chefe final
boss_ativo = False
vida_boss = 20
boss_x = 600
boss_y = 120

# telas especiais
boss_warning = False
tempo_warning = 0

vitoria = False

# pausa
pausado = False

# inimigos
limite_y_inimigo = 450
inimigos = []

for linha in range(4):
    for coluna in range(6):
        x = 150 + coluna * 150
        y = 80 + linha * 100
        inimigos.append([x, y])

explosoes = []

direcao_inimigos = 1
velocidade_inimigos = 2

# tiro jogador
tiro_lazer_jogador = False
laser_x = 0
laser_y = 0
velocidade_laser = 12

# tiros inimigos
tiros_inimigos = []
velocidade_laser_inimigo = 6

fim_de_jogo = False

loop = True

while loop:

    for events in pygame.event.get():
        if events.type == pygame.QUIT:
            loop = False

        if events.type == pygame.KEYDOWN:

            # pausa
            if events.key == pygame.K_p:
                pausado = not pausado

            # aumentar volume
            if events.key == pygame.K_EQUALS or events.key == pygame.K_PLUS:
                volume = min(1.0, volume + 0.1)
                som_tiro.set_volume(volume)
                som_explosao.set_volume(volume)

            # diminuir volume
            if events.key == pygame.K_MINUS:
                volume = max(0.0, volume - 0.1)
                som_tiro.set_volume(volume)
                som_explosao.set_volume(volume)

    teclas = pygame.key.get_pressed()

    # tela aviso boss
    if boss_warning:

        janela.blit(imagem_fundo, (0, 0))

        fonte_grande = pygame.font.SysFont(None, 120)

        texto_warning = fonte_grande.render("⚠ AVISO!! ⚠", True, (255, 0, 0))
        texto_boss = fonte_grande.render("BOSS", True, (255, 255, 255))

        janela.blit(texto_warning, (380, 400))
        janela.blit(texto_boss, (330, 520))

        tempo_warning -= 1

        if tempo_warning <= 0:
            boss_warning = False
            boss_ativo = True

        pygame.display.update()
        clock.tick(60)
        continue

    # tela pausa
    if pausado:
        janela.blit(imagem_fundo, (0, 0))

        fonte_grande = pygame.font.SysFont(None, 80)
        fonte_media = pygame.font.SysFont(None, 40)

        texto_pause = fonte_grande.render("PAUSADO", True, (255, 255, 255))
        texto_volume = fonte_media.render("Volume: + / -", True, (255, 255, 255))
        texto_continuar = fonte_media.render("Pressione P para continuar", True, (255, 255, 255))

        janela.blit(texto_pause, (500, 400))
        janela.blit(texto_volume, (500, 500))
        janela.blit(texto_continuar, (450, 550))

        pygame.display.update()
        clock.tick(60)
        continue

    # CONTROLE DE INVULNERABILIDADE
    if invulneravel:
        tempo_invulneravel -= 1
        if tempo_invulneravel <= 0:
            invulneravel = False

    # movimento jogador
    if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
        posicao_x_jogador -= velocidade_jogador
    if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
        posicao_x_jogador += velocidade_jogador
    if teclas[pygame.K_UP] or teclas[pygame.K_w]:
        posicao_y_jogador -= velocidade_jogador
    if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
        posicao_y_jogador += velocidade_jogador

    # tiro jogador
    if teclas[pygame.K_SPACE] and tiro_lazer_jogador == False:
        tiro_lazer_jogador = True
        som_tiro.play()
        laser_x = posicao_x_jogador + 40
        laser_y = posicao_y_jogador

    # limites
    posicao_x_jogador = max(0, min(posicao_x_jogador, 1180))
    posicao_y_jogador = max(4, min(posicao_y_jogador, 900))

    janela.blit(imagem_fundo, (0, 0))

    laser_rect = pygame.Rect(laser_x, laser_y, 10, 30)

    # inimigos
    for inimigo in inimigos[:]:

        inimigo_rect = pygame.Rect(inimigo[0], inimigo[1], 80, 80)

        if tiro_lazer_jogador and laser_rect.colliderect(inimigo_rect):
            inimigos.remove(inimigo)
            explosoes.append([inimigo[0], inimigo[1], 20])
            som_explosao.play()
            tiro_lazer_jogador = False
            pontuacao += 3
            break

        janela.blit(nave_inimigo, (inimigo[0], inimigo[1]))

    # jogador
    # EFEITO VISUAL DE INVULNERABILIDADE
    if invulneravel and tempo_invulneravel % 10 < 5:  # Piscando
        # Não desenha o jogador (efeito de piscar)
        pass
    else:
        janela.blit(nave_jogador, (posicao_x_jogador, posicao_y_jogador))

    jogador_rect = pygame.Rect(posicao_x_jogador, posicao_y_jogador, 80, 80)

    # VERIFICAÇÃO DE COLISÃO JOGADOR COM INIMIGOS
    if not invulneravel:  # verifica colisão se não estiver invulnerável
        for inimigo in inimigos[:]:
            inimigo_rect = pygame.Rect(inimigo[0], inimigo[1], 80, 80)

            if jogador_rect.colliderect(inimigo_rect):
                vidas -= 1

                # Ativa invulnerabilidade
                invulneravel = True
                tempo_invulneravel = duracao_invulnerabilidade

                if vidas <= 0:
                    fim_de_jogo = True
                    break

    if boss_ativo:

        boss_rect = pygame.Rect(boss_x, boss_y, 200, 200)

        # VERIFICAÇÃO DE COLISÃO JOGADOR COM BOSS (MODIFICADO COM INVULNERABILIDADE)
        if not invulneravel and jogador_rect.colliderect(boss_rect):  # Só verifica se não estiver invulnerável
            vidas -= 3
            posicao_x_jogador = 530
            posicao_y_jogador = 760

            # Ativa invulnerabilidade
            invulneravel = True
            tempo_invulneravel = duracao_invulnerabilidade

            if vidas <= 0:
                fim_de_jogo = True

        if tiro_lazer_jogador and laser_rect.colliderect(boss_rect):
            vida_boss -= 1
            tiro_lazer_jogador = False
            som_explosao.play()

            if vida_boss <= 0:
                boss_ativo = False
                vitoria = True
                explosoes.append([boss_x, boss_y, 100])

        if random.randint(0, 100) < 7:
            som_tiro.play()
            tiros_inimigos.append([boss_x + 100, boss_y + 150])

        janela.blit(nave_inimigo_chefe, (boss_x, boss_y))

    # movimento laser
    if tiro_lazer_jogador:
        janela.blit(lazer_jogador, (laser_x, laser_y))
        laser_y -= velocidade_laser

        if laser_y < 0:
            tiro_lazer_jogador = False

    # movimento inimigos
    trocar_direcao = False

    for inimigo in inimigos:
        inimigo[0] += velocidade_inimigos * direcao_inimigos

        if inimigo[0] <= 0 or inimigo[0] >= 1180:
            trocar_direcao = True

    if trocar_direcao:
        direcao_inimigos *= -1

        pode_descer = True

        for inimigo in inimigos:
            if inimigo[1] + 40 > limite_y_inimigo:
                pode_descer = False
                break

        if pode_descer:
            for inimigo in inimigos:
                inimigo[1] += 40

    # inimigos atiram
    if inimigos:
        if random.randint(0, 100) < 2:
            inimigo = random.choice(inimigos)
            som_tiro.play()
            tiros_inimigos.append([inimigo[0] + 40, inimigo[1] + 40])

    # mover tiros inimigos (MODIFICADO COM INVULNERABILIDADE)
    for tiro in tiros_inimigos[:]:

        tiro[1] += velocidade_laser_inimigo
        tiro_rect = pygame.Rect(tiro[0], tiro[1], 10, 30)

        if tiro_rect.colliderect(jogador_rect):
            if not invulneravel:  # Só perde vida se não estiver invulnerável
                tiros_inimigos.remove(tiro)
                vidas -= 1

                # Ativa invulnerabilidade
                invulneravel = True
                tempo_invulneravel = duracao_invulnerabilidade
            else:
                tiros_inimigos.remove(tiro)  # Remove o tiro mas não perde vida

        elif tiro[1] > 1024:
            tiros_inimigos.remove(tiro)

        else:
            janela.blit(lazer_inimigo, (tiro[0], tiro[1]))

    # explosões
    for explosao in explosoes[:]:
        janela.blit(imagem_explosao, (explosao[0], explosao[1]))
        explosao[2] -= 1

        if explosao[2] <= 0:
            explosoes.remove(explosao)

    # sistema de fases
    if len(inimigos) == 0 and not boss_ativo and fase < max_fases:

        fase += 1

        if fase == max_fases:

            boss_warning = True
            tempo_warning = 180

            vida_boss = 20
            boss_x = 600
            boss_y = 120

        else:

            velocidade_inimigos += 1
            velocidade_laser_inimigo += 1

            for linha in range(4):
                for coluna in range(6):
                    x = 150 + coluna * 150
                    y = 80 + linha * 100
                    inimigos.append([x, y])

    # HUD
    texto_pontos = fonte.render(f'Pontos: {pontuacao}', True, (255, 255, 255))
    janela.blit(texto_pontos, (20, 20))

    texto_vidas = fonte.render(f'Vidas: {vidas}', True, (255, 255, 255))
    janela.blit(texto_vidas, (20, 60))

    texto_fase = fonte.render(f'Fase: Fase: {fase}/{max_fases}', True, (255, 255, 255))
    janela.blit(texto_fase, (20, 100))

    # INDICADOR DE INVULNERABILIDADE
    if invulneravel:
        texto_invulneravel = fonte.render('INVULNERÁVEL', True, (0, 255, 255))
        janela.blit(texto_invulneravel, (20, 140))

    if boss_ativo:
        texto_boss = fonte.render(f'Boss HP: {vida_boss}', True, (255, 50, 50))
        janela.blit(texto_boss, (1000, 20))

        boss_x += 6 * direcao_inimigos

        if boss_x <= 0 or boss_x >= 1080:
            direcao_inimigos *= -1

    # game over
    if vidas <= 0:
        fim_de_jogo = True

    # tela vitória
    if vitoria:

        janela.blit(imagem_fundo, (0, 0))

        fonte_grande = pygame.font.SysFont(None, 100)
        fonte_media = pygame.font.SysFont(None, 50)

        texto_vitoria = fonte_grande.render("PARABÉNS!", True, (255, 255, 0))
        texto_vitoria2 = fonte_media.render("VOCÊ DERROTOU O BOSS", True, (255, 255, 255))
        texto_reiniciar = fonte_media.render("Pressione R para jogar novamente", True, (255, 255, 255))

        janela.blit(texto_vitoria, (460, 380))
        janela.blit(texto_vitoria2, (420, 460))
        janela.blit(texto_reiniciar, (380, 540))

        teclas = pygame.key.get_pressed()

        if teclas[pygame.K_r]:

            pontuacao = 0
            vidas = 15
            fase = 1
            vitoria = False
            boss_ativo = False
            boss_warning = False
            invulneravel = False
            tempo_invulneravel = 0

            inimigos = []

            for linha in range(4):
                for coluna in range(6):
                    x = 150 + coluna * 150
                    y = 80 + linha * 100
                    inimigos.append([x, y])

        pygame.display.update()
        clock.tick(60)
        continue

    if fim_de_jogo:

        janela.blit(imagem_fundo, (0, 0))

        fonte_grande = pygame.font.SysFont(None, 100)
        fonte_media = pygame.font.SysFont(None, 50)

        texto_gameover = fonte_grande.render("FIM DE JOGO", True, (255, 0, 0))
        texto_reiniciar = fonte_media.render("Pressione R para reiniciar", True, (255, 255, 255))

        janela.blit(texto_gameover, (420, 400))
        janela.blit(texto_reiniciar, (400, 500))

        teclas = pygame.key.get_pressed()

        if teclas[pygame.K_r]:

            pontuacao = 0
            vidas = 15
            fase = 1
            posicao_x_jogador = 530
            posicao_y_jogador = 760
            tiros_inimigos = []
            tiro_lazer_jogador = False
            boss_ativo = False
            boss_warning = False
            vida_boss = 20
            velocidade_inimigos = 2
            velocidade_laser_inimigo = 6
            invulneravel = False
            tempo_invulneravel = 0

            inimigos = []
            for linha in range(4):
                for coluna in range(6):
                    x = 150 + coluna * 150
                    y = 80 + linha * 100
                    inimigos.append([x, y])

            fim_de_jogo = False

    clock.tick(60)
    pygame.display.update()

pygame.quit()