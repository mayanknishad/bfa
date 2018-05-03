function getLinkedInAPIKey(){
    var Httpreq = new XMLHttpRequest();
    Httpreq.open("GET", "/api/linkedinapikey", false);
    Httpreq.send(null);
    return JSON.parse(Httpreq.responseText).linkedInApiKey;
}
        
function onLinkedInLoad() {
    IN.Event.on(IN, "auth", getProfileData);
}

// Handle the successful return from the API call
function onSuccess(data) {
    console.log(data);
}

// Handle an error response from the API call
function onError(error) {
    console.log(error);
}

// Use the API call wrapper to request the member's basic profile data
function getProfileData() {
    /*TODO - pass this to our own API to create an advisor*/
    IN.API.Raw("/people/~?format=json").result(onSuccess).error(onError);
}