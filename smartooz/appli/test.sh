
echo "Register.."
curl -X POST -d '{"password":"hugo","username":"papin2","email":"balec"}' http://127.0.0.1:5000/register --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo "Register.."
curl -X POST -d '{"password":"sdlvknxknv","username":"papin2","email":"balec2"}' http://127.0.0.1:5000/register --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo "Login.."
curl -X POST -d '{"password":"hugo","username":"papin2"}' http://127.0.0.1:5000/login --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo "Add place1.."
curl -X POST -d '{"latitude":45.75,"longitude":4.8,"address":"ta mere","openning_hours":"tout le temps","name":"tour papine","description":"flemme","keywords":["sfm", "HOHO"]}' http://127.0.0.1:5000/add-place --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo "Add place1 again.."
curl -X POST -d '{"latitude":45.75,"longitude":4.8,"address":"ta mere","openning_hours":"tout le temps","name":"tour papine","description":"flemme","keywords":["sfm", "HOHO"]}' http://127.0.0.1:5000/add-place --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo "Add place2.."
curl -X POST -d '{"latitude":45.76,"longitude":4.8,"address":"ta 2","openning_hours":"tout le temps","name":"tour sdk","description":"flemme","keywords":["sfm", "c est génial"]}' http://127.0.0.1:5000/add-place --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo "Logout.."
curl http://127.0.0.1:5000/logout --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie

echo "Add place.."
curl -X POST -d '{"password":"hugo","username":"papin2"}' http://127.0.0.1:5000/login --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie