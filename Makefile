.PHONY: image run

image:
	docker build -t herebedragons .

run:
	docker run -v /var/run/postgresql/:/var/run/postgresql/ -p 8000:8000 -e "HBD_SECRET_KEY=test" -e "PORT=8000" -it herebedragons
