import pygame
import random
import sys

# Configurações do Jogo
LARGURA_TELA = 550
ALTURA_TELA = 550
LINHAS = 10
COLUNAS = 10
TAMANHO_CELULA = LARGURA_TELA // COLUNAS
TOTAL_BOMBAS = 15

# Cores
COR_OCULTA = (180, 180, 180)
COR_REVELADA = (220, 220, 220)
COR_LINHA = (100, 100, 100)
COR_BOMBA = (255, 50, 50)
COR_TEXTO = (0, 0, 0)
COR_BANDEIRA = (50, 50, 255)
COR_JOGADOR = (0, 0, 139) # Corpo branco do Bomberman
COR_EXPLOSAO = (255, 150, 0)   # Cor laranja para o efeito de explosão

class CampoMinadoExplosao:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
        pygame.display.set_caption("Vale Minado")
        self.fonte = pygame.font.SysFont("Arial", 18, bold=True)
        self.clock = pygame.time.Clock()
        self.resetar_jogo()

    def resetar_jogo(self):
        self.tabuleiro = [[0 for _ in range(COLUNAS)] for _ in range(LINHAS)]
        self.revelado = [[False for _ in range(COLUNAS)] for _ in range(LINHAS)]
        self.bandeiras = [[False for _ in range(COLUNAS)] for _ in range(LINHAS)]
        self.primeiro_clique = True
        self.game_over = False
        self.vitoria = False
        
        # Posição do jogador
        self.player_r = 0
        self.player_c = 0

        # Sistema de Voo / Explosão
        self.voando = False
        self.modo_explosao = False
        self.voo_x = 0.0
        self.voo_y = 0.0
        self.voo_tamanho = float(TAMANHO_CELULA // 3)
        self.voo_vel_y = -8.0  # Velocidade inicial para cima (mais rápida na explosão)
        self.voo_vel_x = 0.0   # Começa reto e desvia depois

    def plantar_bombas(self, primeiro_r, primeiro_c):
        bombas_plantadas = 0
        while bombas_plantadas < TOTAL_BOMBAS:
            r = random.randint(0, LINHAS - 1)
            c = random.randint(0, COLUNAS - 1)
            if self.tabuleiro[r][c] != -1 and (r != primeiro_r or c != primeiro_c):
                self.tabuleiro[r][c] = -1
                bombas_plantadas += 1

        for r in range(LINHAS):
            for c in range(COLUNAS):
                if self.tabuleiro[r][c] == -1:
                    continue
                self.tabuleiro[r][c] = self.contar_bombas_vizinhas(r, c)

    def contar_bombas_vizinhas(self, r, c):
        contagem = 0
        for i in range(max(0, r - 1), min(LINHAS, r + 2)):
            for j in range(max(0, c - 1), min(COLUNAS, c + 2)):
                if self.tabuleiro[i][j] == -1:
                    contagem += 1
        return contagem

    def revelar_celula(self, r, c):
        if self.revelado[r][c] or self.bandeiras[r][c] or self.voando:
            return

        self.revelado[r][c] = True

        # PISOU NA BOMBA!
        if self.tabuleiro[r][c] == -1:
            self.game_over = True
            self.ativar_voo(por_explosao=True) # Ativa o voo agressivo de explosão
            return

        if self.tabuleiro[r][c] == 0:
            for i in range(max(0, r - 1), min(LINHAS, r + 2)):
                for j in range(max(0, c - 1), min(COLUNAS, c + 2)):
                    self.revelar_celula(i, j)
        
        self.verificar_vitoria()

    def verificar_vitoria(self):
        for r in range(LINHAS):
            for c in range(COLUNAS):
                if self.tabuleiro[r][c] != -1 and not self.revelado[r][c]:
                    return
        self.vitoria = True
        self.ativar_voo(por_explosao=False) # Voa suave comemorando a vitória

    def mover_jogador(self, dr, dc):
        if self.game_over or self.vitoria or self.voando:
            return
        novo_r = self.player_r + dr
        novo_c = self.player_c + dc
        if 0 <= novo_r < LINHAS and 0 <= novo_c < COLUNAS:
            self.player_r = novo_r
            self.player_c = novo_c

    def ativar_voo(self, por_explosao=False):
        if not self.voando:
            self.voando = True
            self.modo_explosao = por_explosao
            # Pega o centro exato da célula onde o jogador explodiu
            self.voo_x = float(self.player_c * TAMANHO_CELULA + TAMANHO_CELULA // 2)
            self.voo_y = float(self.player_r * TAMANHO_CELULA + TAMANHO_CELULA // 2)
            
            if por_explosao:
                self.voo_vel_y = -12.0  # Força de arremesso muito maior
                self.voo_vel_x = random.choice([-3.0, 3.0]) # Arremessa levemente para os lados aleatoriamente

    def atualizar_voo(self):
        if self.voando:
            # Aplica movimento baseado nas velocidades
            self.voo_y += self.voo_vel_y
            self.voo_x += self.voo_vel_x
            
            if self.modo_explosao:
                # Efeito de aproximação ultra rápido devido ao impacto da bomba
                self.voo_tamanho += 2.0 
                # Efeito de gravidade: diminui a subida aos poucos fazendo ele cair depois se quisesse, 
                # mas como ele cresce rápido ele some da tela antes por passar dos limites.
                self.voo_vel_y += 0.2 
            else:
                # Voo normal de vitória (mais suave)
                self.voo_tamanho += 0.6
                self.voo_vel_y = -4.0

    def desenhar(self):
        self.tela.fill(COR_LINHA)
        
        # 1. Desenha o Tabuleiro por baixo
        for r in range(LINHAS):
            for c in range(COLUNAS):
                x = c * TAMANHO_CELULA
                y = r * TAMANHO_CELULA
                rect = pygame.Rect(x, y, TAMANHO_CELULA - 1, TAMANHO_CELULA - 1)

                if self.revelado[r][c]:
                    pygame.draw.rect(self.tela, COR_REVELADA, rect)
                    if self.tabuleiro[r][c] == -1:
                        pygame.draw.circle(self.tela, COR_BOMBA, rect.center, TAMANHO_CELULA // 4)
                    elif self.tabuleiro[r][c] > 0:
                        texto = self.fonte.render(str(self.tabuleiro[r][c]), True, COR_TEXTO)
                        self.tela.blit(texto, texto.get_rect(center=rect.center))
                else:
                    pygame.draw.rect(self.tela, COR_OCULTA, rect)
                    if self.bandeiras[r][c]:
                        pygame.draw.polygon(self.tela, COR_BANDEIRA, [
                            (x + 10, y + 10), (x + TAMANHO_CELULA - 10, y + TAMANHO_CELULA // 2), (x + 10, y + TAMANHO_CELULA - 10)
                        ])

        # 2. Desenha o Personagem acima de tudo
        if self.voando:
            raio = int(self.voo_tamanho)
            pos_centro = (int(self.voo_x), int(self.voo_y))
            
            # Se foi por explosão, pinta o boneco de tons de laranja/fogo enquanto voa
            cor_atual = COR_EXPLOSAO if self.modo_explosao else COR_JOGADOR
            
            pygame.draw.circle(self.tela, cor_atual, pos_centro, raio)
            
            # Olhos acompanhando a proporção do tamanho gigante
            raio_olho = max(2, int(raio * 0.1))
            pygame.draw.circle(self.tela, COR_TEXTO, (pos_centro[0] - int(raio * 0.3), pos_centro[1] - int(raio * 0.1)), raio_olho)
            pygame.draw.circle(self.tela, COR_TEXTO, (pos_centro[0] + int(raio * 0.3), pos_centro[1] - int(raio * 0.1)), raio_olho)
        else:
            # Personagem parado na grade jogando normalmente
            x = self.player_c * TAMANHO_CELULA
            y = self.player_r * TAMANHO_CELULA
            rect = pygame.Rect(x, y, TAMANHO_CELULA - 1, TAMANHO_CELULA - 1)
            pygame.draw.circle(self.tela, COR_JOGADOR, rect.center, TAMANHO_CELULA // 3)
            pygame.draw.circle(self.tela, COR_TEXTO, (rect.centerx - 4, rect.centery - 2), 2)
            pygame.draw.circle(self.tela, COR_TEXTO, (rect.centerx + 4, rect.centery - 2), 2)

        pygame.display.flip()

    def rodar(self):
        while True:
            self.clock.tick(60) # Roda fixo a 60 FPS
            self.atualizar_voo()

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_UP:
                        self.mover_jogador(-1, 0)
                    elif evento.key == pygame.K_DOWN:
                        self.mover_jogador(1, 0)
                    elif evento.key == pygame.K_LEFT:
                        self.mover_jogador(0, -1)
                    elif evento.key == pygame.K_RIGHT:
                        self.mover_jogador(0, 1)
                    elif evento.key == pygame.K_SPACE:
                        if self.primeiro_clique:
                            self.plantar_bombas(self.player_r, self.player_c)
                            self.primeiro_clique = False
                        self.revelar_celula(self.player_r, self.player_c)
                    elif evento.key == pygame.K_f:
                        if not self.voando:
                            if not self.revelado[self.player_r][self.player_c]:
                                self.bandeiras[self.player_r][self.player_c] = not self.bandeiras[self.player_r][self.player_c]
                    
                    # Se o jogo acabou ou o boneco voou para longe, aperte R para reiniciar
                    elif evento.key == pygame.K_r and (self.game_over or self.vitoria or self.voando):
                        self.resetar_jogo()

            self.desenhar()

if __name__ == "__main__":
    CampoMinadoExplosao().rodar()
