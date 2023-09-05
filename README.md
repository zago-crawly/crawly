# Crawly

<p align="center">
<img src="https://github.com/zago-tech/crawly/assets/72471805/42ab71f1-805b-44e1-9c8f-d4c6b827a58a" width="100"/>
</p>

### Платформа для создания, настройки, планирования и мониторинга веб краулеров.

_Framework for creating, configuring, running and monitoring web-crawlers._

_Made with Python._

## Содержание

---

- Описание
- Запуск (WIP)
- Генерация документации

## Описание

---

**Crawly** – платформа для сбора данных из веб-ресурсов с помощью пользовательских схем. Главная задача схем – упростить и ускорить процесс парсинга ресурсов и обработки полученных данных.

Платформа может использоваться для сбора, хранения, обработки и классификации данных.

В отличии от некоторых инструментов для парсинга, написанных на Python, данная платформа – абстракция, которая позволяет не писать код. Тем не менее, данный инструмент применим почти к любому веб ресурсу и является гибким. В центре этого упрощения и гибкости платформы как раз и является схема для парсинга.[^1]

В данной платформе используется микросервисная архитектура с контейнеризацией в [Docker](https://docker.com), а общение между сервисами реализовано с помощью системы сообщений, что позволяет использовать различные конфигурации платформы, или добавлять новый функционал.

[^1]: Схемы и примеры их использования будут описаны далее

## Запуск

---

WIP

## Генерация документации

---

Документация создаётся с помощью инструмента [sphinx](https://www.sphinx-doc.org/en/master/). Все необходимые пакеты прописаны в Pipfile и устанавливаются автоматически при создании окружения проекта.

### HTML

В консоли заходим в папку docs и выполняем команду

`$ make html`

Созданная документация будет расположена в папке docs/build/html. Основной файл - index.html.
PDF

PDF вариант документации создаётся с помощью [LaTeX](https://www.latex-project.org/)

Устанавливаем необходимые пакеты:

```
$ sudo apt-get install texmaker gummi texlive texlive-full texlive-latex-recommended latexdraw intltool-debian lacheck lmodern luatex po-debconf tex-common texlive-binaries texlive-extra-utils texlive-latex-base texlive-latex-base-doc texlive-luatex texlive-xetex texlive-lang-cyrillic texlive-fonts-extra texlive-science texlive-latex-extra texlive-pstricks
```

Заходим в каталог docs/latex и выполняем команды:

`$ pdflatex crawly.tex`

`$ makeindex crawly.idx`

`$ pdflatex crawly.tex`

В этой же папке появится сгенерированный файл документации crawly.pdf.

Для генерации исходных кодов в виде pdf-файла выполняем два раза одну и ту же команду:

$ pdflatex sources.tex
$ pdflatex sources.tex
