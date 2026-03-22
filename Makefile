.PHONY: compile clean update_deps

compile:
	-rmdir /s /q .build 2>nul
	mkdir .build
	if not exist ".deps" @update_deps
	robocopy . .build\ *.py /s /r:3 /w:1 /XD .deps .venv .build || exit 0
	robocopy .deps\ .build\ /e /xf /r:3 /w:1 || exit 0
# 	powershell -Command "Compress-Archive -Path '.build\*' -DestinationPath 'build.zip' -Force"

clean:
	-rmdir /s /q .build 2>nul
	-rmdir /s /q .deps 2>nul


update_deps:
	pip install -r requirements.txt --platform manylinux2014_x86_64 --target .deps --only-binary=:all: --implementation cp --upgrade
