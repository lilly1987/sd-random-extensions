# sd-random-extensions
 
마음대로 개조 및 배포 가능  


# 설치법

![2022-11-26 17 34 32](https://user-images.githubusercontent.com/20321215/204080575-9817d380-2d5d-434e-995c-fa69c8eca444.png)


# 랜덤 항목

![2022-11-26 17 33 58](https://user-images.githubusercontent.com/20321215/204080561-2dd916e2-1593-4955-8a87-765af1f9762e.png)

- step
- CFG = int 형으로 처리. 즉 소수점 처리 안함.(누가 개조해줘)
- denoising = denoising1 ~ denoising2 사이의 랜덧값. img2img 전용.
- width = width1 ~ width2 사이의 랜덧값. 64의 배수로 자동 처리
- height = height1 ~ height2 사이의 랜덧값. 64의 배수로 자동 처리
- fix width height direction = 특정 방향으로 회전. 예를들어 가로보다 세로가 길 경우 가로방향으로 회전.
- Sampling Random = 샘플링 선택한것중 랜덤
- fixed_seeds = 시드를 -1로 고정할지 여부


# 무한 반복 방법

WEBUI의 자체 기능.  

- 무한 반복 시작  

![2022-11-26 17 45 41](https://user-images.githubusercontent.com/20321215/204080546-809fff86-7674-4730-97cf-006a57fed282.png)


- 무한 반복 취소  

![2022-11-26 17 48 01](https://user-images.githubusercontent.com/20321215/204080544-47c134a5-b450-48e9-81c9-72d94275e162.png)


# 참조

https://gist.github.com/camenduru/9ec5f8141db9902e375967e93250860f  
https://github.com/adieyal/sd-dynamic-prompts  

