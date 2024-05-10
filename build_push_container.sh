# shell script to build and push container

echo "building docker container"
docker build . -t wedding-website

echo "Tagging and pushing container to Artifact Registry: /wedding-website-409618/website-containers/wedding-website"

docker tag wedding-website us-central1-docker.pkg.dev/wedding-website-409618/website-containers/wedding-website
docker push us-central1-docker.pkg.dev/wedding-website-409618/website-containers/wedding-website
