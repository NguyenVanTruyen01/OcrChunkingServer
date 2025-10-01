run:
	cd docker && docker compose up -d && cd -

rebuild:
	cd docker && docker compose up --build -d && cd -

exec:
	docker exec -it ocr-chunking-api bash
