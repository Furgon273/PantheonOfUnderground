import pygame
import random as RNG
import math as mat


class Bullet:
    def __init__(self, StartX, StartY, BulletType, BulletData, Image, ImageSizeX, ImageSizeY, HitboxSizeX, HitboxSizeY,
                 Damage, InvFrames, GrazingPotential, DamageType='White'):
        self.PositionX = StartX
        self.PositionY = StartY
        self.Type = BulletType
        self.Image = Image
        self.NeedsDelete = False
        self.ImageSizeX = ImageSizeX
        self.ImageSizeY = ImageSizeY
        self.HitboxSizeX = HitboxSizeX
        self.HitboxSizeY = HitboxSizeY
        self.Damage = Damage
        self.InvFrames = InvFrames
        self.GrazingPotential = GrazingPotential
        self.DamageType = DamageType
        if self.Type == 'Base':
            self.Direction = BulletData[0]
            self.Speed = BulletData[1]
        if self.Type == 'NapstablookTear':
            self.Direction = BulletData[0]
            self.Stage = BulletData[1]
        if self.Type == 'SinusX':
            self.Speed = BulletData[0]
            self.SinusValueCoof = BulletData[1]
            self.SinusArgumentCoof = BulletData[2]
            self.SinusArgumentAdder = BulletData[3]
            self.ImaginaryPositionY = self.PositionY
            self.PositionY += mat.sin(
                self.PositionX * self.SinusArgumentCoof + self.SinusArgumentAdder) * self.SinusValueCoof
        if self.Type == 'RorrimBullet':
            self.MaxSpeed = BulletData[0]
            self.LeftLoops = BulletData[1]
            self.CurSpeed = 0
            self.IsAccelerating = True
            self.Direction = AimToPlayer(self.PositionX, self.PositionY)
        if self.Type == 'Falling':
            self.Xv = BulletData[0]
            self.Yv = BulletData[1]
            self.Gravity = BulletData[2]
            self.SpawnOnGround = BulletData[3]

    def CheckCollision(self):
        global Lives, InvFrames, TP, GrazingAnimation
        if self.DamageType == 'Blue' and not PlayerIsMoving:
            return
        if pygame.Rect(self.PositionX - self.HitboxSizeX / 2, self.PositionY - self.HitboxSizeY / 2, self.HitboxSizeX,
                       self.HitboxSizeY).colliderect(
            pygame.Rect(PlayerX - 10, PlayerY - 10, 20, 20)) and InvFrames == 0:
            Lives -= self.Damage
            InvFrames = self.InvFrames
            self.NeedsDelete = True
        if pygame.Rect(self.PositionX - self.HitboxSizeX / 2, self.PositionY - self.HitboxSizeY / 2, self.HitboxSizeX,
                       self.HitboxSizeY).colliderect(
            pygame.Rect(PlayerX - 20, PlayerY - 20, 40, 40)) and InvFrames == 0:
            TP += self.GrazingPotential
            if self.GrazingPotential >= 0.1:
                GrazingAnimation = 7
                self.GrazingPotential /= 100
            if TP > 100:
                TP = 100

    def Draw(self, DrawWindow):
        DrawWindow.blit(self.Image,
                        pygame.Rect(self.PositionX - self.ImageSizeX / 2, self.PositionY - self.ImageSizeY / 2,
                                    self.ImageSizeX, self.ImageSizeY))

    def Move(self):
        if self.Type == 'Base':
            self.PositionX -= self.Speed * mat.sin(self.Direction)
            self.PositionY -= self.Speed * mat.cos(self.Direction)
        if self.Type == 'NapstablookTear':
            if self.Stage == 1:
                self.PositionY += 5
                if self.PositionY >= BoxCenterY + BoxSizeY - self.HitboxSizeY:
                    self.Stage += 1
            elif self.Stage == 2:
                self.PositionX += 3 * self.Direction
                if abs(self.PositionX - BoxCenterX) >= BoxSizeX - self.HitboxSizeX:
                    self.Stage += 1
            elif self.Stage == 3:
                self.PositionY -= 3
                if self.PositionY <= BoxCenterY - BoxSizeY + self.HitboxSizeY:
                    self.Stage += 1
            elif self.Stage == 4:
                self.PositionX -= 3 * self.Direction
                if abs(self.PositionX - PlayerX) <= 10:
                    self.Stage += 1
            elif self.Stage == 5:
                self.PositionY += 2
        if self.Type == 'SinusX':
            self.PositionX += self.Speed
            self.PositionY = self.ImaginaryPositionY + mat.sin(
                self.PositionX * self.SinusArgumentCoof + self.SinusArgumentAdder) * self.SinusValueCoof
        if self.Type == 'RorrimBullet':
            self.PositionX -= self.CurSpeed * mat.sin(self.Direction)
            self.PositionY -= self.CurSpeed * mat.cos(self.Direction)
            if self.IsAccelerating:
                self.CurSpeed += self.MaxSpeed * 0.02
                if self.CurSpeed >= self.MaxSpeed and self.LeftLoops > 0:
                    self.IsAccelerating = False
            else:
                self.CurSpeed -= self.MaxSpeed * 0.02
                if self.CurSpeed <= 0:
                    self.IsAccelerating = True
                    self.LeftLoops -= 1
                    self.Direction = AimToPlayer(self.PositionX, self.PositionY)
                    self.GrazingPotential = 0.5
        if self.Type == 'Falling':
            self.PositionX += self.Xv
            self.PositionY -= self.Yv
            self.Yv -= self.Gravity
            if self.PositionY >= BoxCenterY + BoxSizeX - self.ImageSizeX / 2 and self.Yv <= 0 and len(
                    self.SpawnOnGround):
                for SpawnedBullet in self.SpawnOnGround:
                    SpawnedBullet.PositionX = self.PositionX
                    SpawnedBullet.PositionY = self.PositionY
                    Bullets.append(SpawnedBullet)
                self.NeedsDelete = True
        self.CheckCollision()
        self.Draw(Window)
        if not (-100 < self.PositionX < 700 and -100 < self.PositionY < 700):
            self.NeedsDelete = True

    def NextFrame(self, DrawWindow):
        self.Move()
        self.Draw(DrawWindow)


class Laser:
    def __init__(self, PositionX, PositionY, Direction, Width, WarningImage, WarningFrames, ActiveImage, ActiveFrames,
                 ImageSize, Damage, InvFrames, GrazingPotential):
        self.PositionX = PositionX
        self.PositionY = PositionY
        self.WarningImage = WarningImage
        self.AcctiveImage = ActiveImage
        self.ImageSize = ImageSize
        self.Direction = Direction
        self.Width = Width
        self.WarningFrames = WarningFrames
        self.ActiveFrames = ActiveFrames
        self.Damage = Damage
        self.InvFrames = InvFrames
        self.GrazingPotential = GrazingPotential
        self.NeedsDelete = False

    def NextFrame(self, DrawWindow):
        global Lives, InvFrames, TP, GrazingAnimation
        if self.WarningFrames > 0:
            Image = RotateImage(self.WarningImage, self.Direction)
            self.WarningFrames -= 1
        elif self.ActiveFrames > 0:
            Image = RotateImage(self.AcctiveImage, self.Direction)
            self.ActiveFrames -= 1
            C = self.PositionY * mat.sin(self.Direction) - self.PositionX * mat.cos(self.Direction)
            if mat.fabs(PlayerX * mat.cos(self.Direction) - PlayerY * mat.sin(
                    self.Direction) + C) <= self.Width + 5 and InvFrames == 0:
                Lives -= self.Damage
                InvFrames = self.InvFrames
            if mat.fabs(PlayerX * mat.cos(self.Direction) - PlayerY * mat.sin(
                    self.Direction) + C) <= self.Width + 15 and InvFrames == 0:
                TP += self.GrazingPotential
                if self.GrazingPotential >= 0.1:
                    GrazingAnimation = 7
                    self.GrazingPotential /= 100
                if TP > 100:
                    TP = 100
        else:
            self.NeedsDelete = True
            return
        DrawWindow.blit(Image, pygame.Rect(self.PositionX - self.ImageSize / 2, self.PositionY - self.ImageSize / 2,
                                           self.ImageSize, self.ImageSize))


class WerewireArmy:
    def __init__(self, StartPhase=0):
        self.BossHP = [500, 500, 500]
        self.BossCooldown = [120, 80, 50]
        self.PlayerTarget = 0
        self.Phase = StartPhase
        self.Theme = "OST/WerewireArmyTheme.mp3"

    def Attack(self, Index):
        Callibration = RNG.randint(-15, 15) / 180 * mat.pi
        WerewireBulletImage = GetImage('Images/WerewireBullet.png', 30, 30)
        for BulletNumber in range(-2, 3):
            Bullets.append(Bullet(216 + 84 * Index, 180, 'Base',
                                  [AimToPlayer(216 + 84 * Index, 180) - Callibration - mat.pi * BulletNumber / 6, 4],
                                  WerewireBulletImage, 30, 30, 20, 20, 30, 70, 2))
        self.BossCooldown[Index] = RNG.randint(40, 70)

    def Draw(self, Index, DrawWindow):
        WerewireImage = GetImage('Images/Werewire.png', 84, 270)
        PlayerTargetImage = GetImage('Images/Aim.png', 54, 36)
        if self.BossHP[Index] > 0:
            DrawWindow.blit(WerewireImage, pygame.Rect(Index * 84 + 174, 0, 84, 270))
            pygame.draw.rect(DrawWindow, 'red', pygame.Rect(Index * 84 + 191, 270, 50, 20))
            pygame.draw.rect(DrawWindow, 'green', pygame.Rect(Index * 84 + 191, 270, self.BossHP[Index] / 10, 20))
        if Index == self.PlayerTarget // 20:
            DrawWindow.blit(PlayerTargetImage, pygame.Rect(Index * 84 + 189, 150, 54, 36))

    def CheckDeath(self):
        if self.BossHP[0] <= 0 and self.BossHP[1] <= 0 and self.BossHP[2] <= 0:
            self.Phase = -1

    def NextFrame(self):
        if len(AttackTimings) == 0:
            self.PlayerTarget += 1
            if self.PlayerTarget >= 60:
                self.PlayerTarget = 0
        for WerewireNumber in range(0, 3):
            self.Draw(WerewireNumber, Window)
            if self.BossHP[WerewireNumber] <= 0:
                continue
            if self.BossCooldown[WerewireNumber] == 0:
                self.Attack(WerewireNumber)
            else:
                self.BossCooldown[WerewireNumber] -= 1
        self.CheckDeath()

    def TakeDamage(self, DamageTaken):
        self.BossHP[self.PlayerTarget // 20] -= DamageTaken


class Napstablook:
    def __init__(self, StartPhase=0):
        self.BossHP = 1200
        self.BossCooldown = 20
        self.Position = 0
        self.Phase = StartPhase
        self.Theme = "OST/NapstablookTheme.mp3"

    def Attack(self):
        NapstablookBulletImage = GetImage('Images/NapstablookBullet.png', 40, 40)
        if RNG.randint(1, 100) <= 80:
            Bullets.append(Bullet(300 + self.Position, 140, 'Base', [RNG.randint(-314, 314) / 600 - mat.pi, 3],
                                  NapstablookBulletImage, 40, 40, 10, 10, 45, 80, 1))
            Bullets.append(Bullet(320 + self.Position, 150, 'Base', [RNG.randint(-314, 314) / 600 - mat.pi, 3],
                                  NapstablookBulletImage, 40, 40, 10, 10, 45, 80, 1))
            self.BossCooldown = 20
        else:
            Bullets.append(
                Bullet(300 + self.Position, 140, 'NapstablookTear', [-1, 1], NapstablookBulletImage, 40, 40, 10, 10, 45,
                       80, 1))
            Bullets.append(
                Bullet(320 + self.Position, 150, 'NapstablookTear', [1, 1], NapstablookBulletImage, 40, 40, 10, 10, 45,
                       80, 1))
            self.BossCooldown = 40

    def Draw(self, DrawWindow):
        NapstablookImage = GetImage('Images/Napstablook.png', 160, 180)
        DrawWindow.blit(NapstablookImage, pygame.Rect(225 + self.Position, 90, 150, 180))
        pygame.draw.rect(DrawWindow, 'red', pygame.Rect(150, 270, 300, 20))
        pygame.draw.rect(DrawWindow, 'green', pygame.Rect(150, 270, self.BossHP / 4, 20))

    def CheckDeath(self):
        if self.BossHP <= 0:
            self.Phase = -1

    def NextFrame(self):
        if abs(self.Position) >= 50:
            self.Position += 1
        if self.Position % 2 == 0:
            self.Position += 2
        else:
            self.Position -= 2
        self.Draw(Window)
        if self.BossCooldown == 0:
            self.Attack()
        else:
            self.BossCooldown -= 1
        self.CheckDeath()

    def TakeDamage(self, DamageTaken):
        self.BossHP -= DamageTaken


class YellowMercenaries:
    def __init__(self, StartPhase=0):
        self.FlierHP = 200
        self.RorrimHP = 800
        self.CrispyScrollHP = 500
        self.FlierCooldown = 30
        self.RorrimCooldown = 70
        self.CrispyScrollCooldown = 50
        self.PlayerTarget = 0
        self.Phase = StartPhase
        self.Theme = "OST/YellowMercenariesTheme.mp3"

    def Attack(self):
        FlierBulletImage = GetImage('Images/FlierBullet.png', 25, 20)
        RorrimShardImage = GetImage('Images/RorrimShard.png', 25, 25)
        RorrimMirrorImage = GetImage('Images/RorrimMirror.png', 42, 70)
        CrispyScrollBulletImage = GetImage('Images/CrispyScrollBullet.png', 60, 47)
        CrispyScrollLaserImage = GetImage('Images/CrispyScrollLaser.png', 400, 400)
        CrispyScrollWarningImage = GetImage('Images/CrispyScrollWarning.png', 400, 400)
        if self.FlierCooldown <= 0 < self.FlierHP:
            if RNG.randint(0, 100) > 50:
                Bullets.append(
                    Bullet(100, RNG.randint(300, 500), 'SinusX', [2, 20, 3, RNG.randint(0, 62) / 10], FlierBulletImage,
                           25, 20, 2, 2, 20, 100, 0.5))
            else:
                Bullets.append(
                    Bullet(500, RNG.randint(300, 500), 'SinusX', [-2, 20, 3, RNG.randint(0, 62) / 10], FlierBulletImage,
                           25, 20, 2, 2, 20, 100, 0.5))
            self.FlierCooldown = 70
        if self.RorrimCooldown <= 0 < self.RorrimHP:
            if RNG.randint(0, 100) > 50:
                Bullets.append(
                    Bullet(190 + RNG.randint(0, 1) * 220, 290 + RNG.randint(0, 1) * 220, 'RorrimBullet', [3, 4],
                           RorrimShardImage, 25, 25, 2, 2, 50, 60, 0.5))
            else:
                SpawnOnGround = []
                PositionX = RNG.randint(220, 380)
                for Shard in range(3):
                    SpawnOnGround.append(
                        Bullet(-1, -1, 'Falling', [RNG.randint(210 - PositionX, 390 - PositionX) / 100, 5, 0.1, []],
                               RorrimShardImage, 25, 25, 2, 2, 50, 60, 0.5))
                Bullets.append(
                    Bullet(PositionX, 250, 'Falling', [0, 2, 0.1, SpawnOnGround], RorrimMirrorImage, 42, 70, 20, 50, 80,
                           80, 1.5))
            self.RorrimCooldown = 165
        if self.CrispyScrollCooldown <= 0 < self.CrispyScrollHP:
            if RNG.randint(0, 100) > 50:
                Bullets.append(
                    Laser(320, PlayerY, -mat.pi / 2, 30, CrispyScrollWarningImage, 50, CrispyScrollLaserImage, 14, 400,
                          100, 80, 2))
            else:
                PositionX = RNG.randint(220, 380)
                SpawnOnGround = [
                    Bullet(-1, -1, 'Falling', [RNG.randint(210 - PositionX, 390 - PositionX) / 80, 8, 0.2, []],
                           CrispyScrollBulletImage, 60, 47, 30, 17, 70, 60, 1)]
                Bullets.append(
                    Bullet(PositionX, 250, 'Falling', [0, 1, 0.2, SpawnOnGround], CrispyScrollBulletImage, 60, 47, 30,
                           17, 70, 60, 1))
            self.CrispyScrollCooldown = 125
        MercenariesAlive = 3.5
        if self.FlierHP <= 0:
            MercenariesAlive -= 1
        if self.RorrimHP <= 0:
            MercenariesAlive -= 1
        if self.CrispyScrollHP <= 0:
            MercenariesAlive -= 1
        self.FlierCooldown -= 3.5 / MercenariesAlive
        self.RorrimCooldown -= 3.5 / MercenariesAlive
        self.CrispyScrollCooldown -= 3.5 / MercenariesAlive

    def Draw(self, DrawWindow):
        FlierImage = GetImage('Images/Flier.png', 60, 64)
        RorrimImage = GetImage('Images/Rorrim.png', 128, 150)
        CrispyScrollImage = GetImage('Images/CrispyScroll.png', 120, 90)
        CrispyScrollImage = pygame.transform.scale(CrispyScrollImage, (120, 90))
        PlayerTargetImage = GetImage('Images\Aim.png', 54, 36)
        if self.FlierHP > 0:
            DrawWindow.blit(FlierImage, pygame.Rect(170, 170, 60, 64))
            pygame.draw.rect(DrawWindow, 'red', pygame.Rect(170, 270, 60, 20))
            pygame.draw.rect(DrawWindow, 'green', pygame.Rect(170, 270, self.FlierHP / 10 * 3, 20))
        if self.RorrimHP > 0:
            DrawWindow.blit(RorrimImage, pygame.Rect(236, 120, 128, 150))
            pygame.draw.rect(DrawWindow, 'red', pygame.Rect(270, 270, 60, 20))
            pygame.draw.rect(DrawWindow, 'green', pygame.Rect(270, 270, self.RorrimHP / 40 * 3, 20))
        if self.CrispyScrollHP > 0:
            DrawWindow.blit(CrispyScrollImage, pygame.Rect(340, 170, 120, 90))
            pygame.draw.rect(DrawWindow, 'red', pygame.Rect(370, 270, 60, 20))
            pygame.draw.rect(DrawWindow, 'green', pygame.Rect(370, 270, self.CrispyScrollHP / 25 * 3, 20))
        DrawWindow.blit(PlayerTargetImage, pygame.Rect(173 + self.PlayerTarget // 20 * 100, 200, 54, 36))

    def NextFrame(self):
        if len(AttackTimings) == 0:
            self.PlayerTarget += 1
            if self.PlayerTarget >= 60:
                self.PlayerTarget = 0
        self.Draw(Window)
        self.Attack()
        self.CheckDeath()

    def TakeDamage(self, DamageTaken):
        if self.PlayerTarget < 20:
            self.FlierHP -= DamageTaken
        elif self.PlayerTarget < 40:
            self.RorrimHP -= DamageTaken
        else:
            self.CrispyScrollHP -= DamageTaken

    def CheckDeath(self):
        if self.FlierHP <= 0 and self.RorrimHP <= 0 and self.CrispyScrollHP <= 0:
            self.Phase = -1


class Doggo:
    def __init__(self, StartPhase=0):
        self.BossHP = 700
        self.Cooldown = 21
        self.Phase = StartPhase
        self.Theme = "OST/WerewireArmyTheme.mp3"
        self.Direction = 1

    def Attack(self):
        DoggoSwordImage = GetImage('Images/DoggoSword.png', 52, 200)
        global PossibleAttackBox, BoxSizeX
        if self.Cooldown == 21:
            PossibleAttackBox = [RNG.randint(100, 480), RNG.randint(300, 480)]
            PossibleAttackBox += [PossibleAttackBox[0] + 20, PossibleAttackBox[1] + 20]
            BoxSizeX = 200
        if self.Cooldown == 0:
            Bullets.append(Bullet(300 + 250 * self.Direction, 400, 'Base', [mat.pi * self.Direction / 2, 7], DoggoSwordImage, 52, 200, 20, 200, 30, 10, 0.5, DamageType='Blue'))
            self.Cooldown = 20
        self.Cooldown -= 1

    def Draw(self, DrawWindow):
        DoggoImage = GetImage('Images/Doggo.png', 170, 270)
        PossibleAttackBoxImage = GetImage('Images/PossibleAttackBox.png', 20, 20)
        DrawWindow.blit(DoggoImage, pygame.Rect(215, 0, 170, 270))
        DrawWindow.blit(PossibleAttackBoxImage, pygame.Rect(PossibleAttackBox[0], PossibleAttackBox[1], 20, 20))
        pygame.draw.rect(DrawWindow, 'red', pygame.Rect(125, 270, 350, 20))
        pygame.draw.rect(DrawWindow, 'green', pygame.Rect(125, 270, self.BossHP / 2, 20))

    def NextFrame(self):
        self.Draw(Window)
        self.Attack()
        self.CheckDeath()

    def TakeDamage(self, DamageTaken):
        global PossibleAttackBox
        self.BossHP -= DamageTaken
        self.Direction *= -1
        PossibleAttackBox = [RNG.randint(100, 480), RNG.randint(300, 480), 20, 20]

    def CheckDeath(self):
        global PossibleAttackBox, BoxSizeX
        if self.BossHP <= 0:
            self.Phase = -1
            PossibleAttackBox = [0, 0, 600, 600]
            BoxSizeX = 100


def AimToPlayer(PositionX, PositionY):
    if PositionY <= PlayerY:
        return mat.atan((PositionX - PlayerX + 0.0001) / (PositionY - PlayerY + 0.0001)) + mat.pi
    return mat.atan((PositionX - PlayerX + 0.0001) / (PositionY - PlayerY + 0.0001))


def RotateImage(Image, Angle):
    OriginalRect = Image.get_rect()
    RotatedImage = pygame.transform.rotate(Image, Angle / mat.pi * 180)
    RotatedRect = OriginalRect.copy()
    RotatedRect.center = RotatedImage.get_rect().center
    RotatedImage = RotatedImage.subsurface(RotatedRect).copy()
    return RotatedImage


def GetImage(ImageFile, SizeX, SizeY):
    Image = pygame.image.load(ImageFile)
    Image = pygame.transform.scale(Image, (SizeX, SizeY))
    return Image


pygame.init()
n = 0
Run = True
Lives = 1000
DefaultSpeedhack = 1
Speedhack = DefaultSpeedhack
Font = pygame.font.SysFont('Pixel', 35)
Window = pygame.display.set_mode((600, 600))
pygame.display.set_caption('')
Clock = pygame.time.Clock()
Pantheons = [[WerewireArmy(), Napstablook(), YellowMercenaries(), Doggo()]]
Bullets = []
AttackEffects = []
AttackTimings = []
AttackCooldown = 300
CurrentBoss = 0
PantheonID = 0
CutsceneID = 0
GrazingAnimation = 0
TP = 0
HoldingZ = False
BoxCenterX = 300
BoxCenterY = 400
PossibleAttackBox = [0, 0, 600, 600]
PlayerX = BoxCenterX
PlayerY = BoxCenterY
BoxSizeX = 100
BoxSizeY = 100
InvFrames = 0
PlayerNormalImage = GetImage('Images/PlayerNormal.png', 20, 20)
ChargedAttackImage = GetImage('Images/ChargedAttack.png', 20, 20)
GrazeboxImage = GetImage('Images/Grazebox.png', 40, 40)
AttackBarImage = GetImage('Images/AttackBar.png', 300, 60)
pygame.mixer.music.load(Pantheons[PantheonID][CurrentBoss].Theme)
pygame.mixer.music.play(-1)
while Run:
    if Pantheons[PantheonID][CurrentBoss].Phase == -1:
        CurrentBoss += 1
        pygame.mixer.music.load(Pantheons[PantheonID][CurrentBoss].Theme)
        pygame.mixer.music.play(-1)
    PlayerIsMoving = False
    n += 1
    GrazingAnimation -= 1
    if InvFrames != 0:
        InvFrames -= 1
    if AttackCooldown != 0:
        AttackCooldown -= 1
    clicked = False
    for i in pygame.event.get():
        KeysPressed = pygame.key.get_pressed()
        if i.type == pygame.QUIT:
            run = False
    if KeysPressed[pygame.K_RIGHT] or KeysPressed[pygame.K_d]:
        PlayerX += 4
        PlayerIsMoving = True
    if KeysPressed[pygame.K_LEFT] or KeysPressed[pygame.K_a]:
        PlayerX -= 4
        PlayerIsMoving = True
    if KeysPressed[pygame.K_DOWN] or KeysPressed[pygame.K_s]:
        PlayerY += 4
        PlayerIsMoving = True
    if KeysPressed[pygame.K_UP] or KeysPressed[pygame.K_w]:
        PlayerY -= 4
        PlayerIsMoving = True
    if PlayerX > BoxCenterX + BoxSizeX - 10:
        PlayerX = BoxCenterX + BoxSizeX - 10
    if PlayerX < BoxCenterX - BoxSizeX + 10:
        PlayerX = BoxCenterX - BoxSizeX + 10
    if PlayerY > BoxCenterY + BoxSizeY - 10:
        PlayerY = BoxCenterY + BoxSizeY - 10
    if PlayerY < BoxCenterY - BoxSizeY + 10:
        PlayerY = BoxCenterY - BoxSizeY + 10
    Speedhack = DefaultSpeedhack
    if KeysPressed[pygame.K_c] and TP >= 0.5:
        TP -= 0.5
        Speedhack = DefaultSpeedhack * 0.4
    if KeysPressed[pygame.K_z] and not HoldingZ:
        if AttackCooldown == 0 and PossibleAttackBox[0] <= PlayerX <= PossibleAttackBox[0] + PossibleAttackBox[2] and PossibleAttackBox[1] <= PlayerY <= PossibleAttackBox[1] + PossibleAttackBox[3]:
            AttackTimings = [n + 50]
            for AttackNumber in range(0, 3):
                AttackTimings.append(AttackTimings[-1] + RNG.randint(12, 24))
            AttackDamage = 0
            AttackCritMultiplier = 1
            AttackCooldown = 300
            HoldingZ = True
        elif len(AttackTimings) != 0:
            AttackDamage += max(0, 25 - 2 * abs(n - AttackTimings[0]))
            if n == AttackTimings[0]:
                AttackCritMultiplier += 0.5
            elif abs(n - AttackTimings[0]) > 12:
                AttackCritMultiplier -= 0.25
            AttackEffects.append([297 + 6 * (n - AttackTimings[0]), n + 20])
            del AttackTimings[0]
            HoldingZ = True
            if len(AttackTimings) == 0:
                Pantheons[PantheonID][CurrentBoss].TakeDamage(AttackDamage * AttackCritMultiplier)
    if not KeysPressed[pygame.K_z]:
        HoldingZ = False
    if len(AttackTimings) > 0 and n > AttackTimings[0] + 100:
        del AttackTimings[0]
        AttackCritMultiplier -= 0.25
        if len(AttackTimings) == 0:
            Pantheons[PantheonID][CurrentBoss].TakeDamage(AttackDamage * AttackCritMultiplier)
    if len(AttackEffects) > 0 and n >= AttackEffects[0][1]:
        del AttackEffects[0]
    BulletsToDelete = []
    for i in range(0, len(Bullets)):
        if Bullets[i].NeedsDelete:
            BulletsToDelete.append(i)
    for i in BulletsToDelete[::-1]:
        del Bullets[i]
    Window.fill((0, 0, 0))
    if CurrentBoss == 'Cutscene':
        pass  # TODO
    else:
        Pantheons[PantheonID][CurrentBoss].NextFrame()
    if GrazingAnimation > 0:
        Window.blit(GrazeboxImage, pygame.Rect(PlayerX - 20, PlayerY - 20, 40, 40))
    pygame.draw.rect(Window, 'white',
                     pygame.Rect(BoxCenterX - 5 - BoxSizeX, BoxCenterY - 5 - BoxSizeY, BoxSizeX * 2 + 10,
                                 BoxSizeY * 2 + 10), 10)
    pygame.draw.rect(Window, 'red', pygame.Rect(0, 580, 600, 20))
    pygame.draw.rect(Window, 'yellow', pygame.Rect(0, 580, Lives * 0.6, 20))
    pygame.draw.rect(Window, 'orange', pygame.Rect(0, 450 - 3 * TP, 20, 3 * TP))
    pygame.draw.rect(Window, 'white', pygame.Rect(-5, 145, 30, 310), 10)
    for i in Bullets:
        i.NextFrame(Window)
    if Lives <= 0:
        Run = False
    if InvFrames == 0 or n % 14 < 7:
        if AttackCooldown > 0:
            Window.blit(PlayerNormalImage, pygame.Rect(PlayerX - 10, PlayerY - 10, 20, 20))
        else:
            Window.blit(ChargedAttackImage, pygame.Rect(PlayerX - 10, PlayerY - 10, 20, 20))
    if len(AttackTimings) > 0:
        Window.blit(AttackBarImage, pygame.Rect(150, 520, 300, 60))
    for AttackTiming in AttackTimings:
        pygame.draw.rect(Window, 'white', pygame.Rect(297 + 6 * (n - AttackTiming), 520, 6, 60))
    for AttackEffect in AttackEffects:
        if AttackEffect[0] == 297:
            pygame.draw.rect(Window, pygame.Color(255, 255, 0),
                             pygame.Rect(AttackEffect[0], 550 - 1.5 * (AttackEffect[1] - n), 6,
                                         3 * (AttackEffect[1] - n)))
        elif abs(AttackEffect[0] - 297) <= 72:
            pygame.draw.rect(Window, pygame.Color(0, 255, 255),
                             pygame.Rect(AttackEffect[0], 550 - 1.5 * (AttackEffect[1] - n), 6,
                                         3 * (AttackEffect[1] - n)))
        else:
            pygame.draw.rect(Window, pygame.Color(255, 0, 0),
                             pygame.Rect(AttackEffect[0], 550 - 1.5 * (AttackEffect[1] - n), 6,
                                         3 * (AttackEffect[1] - n)))
    pygame.display.update()
    Clock.tick(60 * Speedhack)
pygame.quit()
