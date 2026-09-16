# Bouwrecept voor de silver-tier van estafette, gedraaid door het eigen harnas
# (src/estafette/harness/podman.py, invariant I4).
#
# De run-fase draait met `--network=none`, `--read-only` en `--env-host=false`.
# Dat stelt drie eisen aan dit image, en elke regel hieronder dient er een:
#
#   - alles wat netwerk nodig heeft gebeurt in de BOUW-fase (pip install), niet
#     bij het draaien;
#   - niets schrijft naar het bestandssysteem tijdens het draaien, vandaar
#     PYTHONDONTWRITEBYTECODE (anders probeert Python .pyc weg te schrijven op
#     een read-only root);
#   - de opdracht eindigt uit zichzelf met 0, passend bij `readiness: exits-zero`
#     in transfer.yaml. `estafette --help` doet precies dat en raakt niets aan.
#
# De basis staat op een versietag en niet op een digest. Dat is bewust
# onaf: pinnen op digest hoort bij dit project (het gaat over
# reproduceerbaarheid), maar een digest die niemand heeft kunnen bouwen en
# controleren is een cijfer zonder dekking. Pin hem zodra dit image ergens
# écht gebouwd is.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /src
COPY . /src

RUN pip install --no-cache-dir .

# Niet als root draaien: het harnas dwingt isolatie af, maar een image dat daar
# zelf aan meewerkt is een betere buur.
USER 65534:65534

ENTRYPOINT ["estafette"]
CMD ["--help"]
