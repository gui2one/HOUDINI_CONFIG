//find index of maximum value in an array
int findMaxIndex(int values[]){
    //float values[] = array(0.5,0.8,0.6,15);
    float myMax = max(values);
    int index = -1;
    for(int i=0; i< len(values); i++){
        if(values[i] == myMax){
        
            //printf("value : %s  - index : %s\n",myMax, i);
            index = i;
            break;
        }
    }
    
    return index;
}

int findMaxIndex(float values[]){
    //float values[] = array(0.5,0.8,0.6,15);
    float myMax = max(values);
    int index = -1;
    for(int i=0; i< len(values); i++){
        if(values[i] == myMax){
        
            //printf("value : %s  - index : %s\n",myMax, i);
            index = i;
            break;
        }
    }
    
    return index;
}

void smoothStep(int _samples; int _startSample; float _startHeight; float _height; int _primNum){

    //_startSample /= 2;
    for(int i =0; i<_samples-1; i++){
        float posx = (_startSample+i)*0.02;
        float posy = fit01(smooth(0.0,1.0,float(i)/(_samples-1)),_startHeight, _startHeight + _height);
        int pt = addpoint(geoself(),set(posx,posy,0));
        setpointattrib(geoself(), "primNum",pt,_primNum);
        //_startSample += 1;
    }

}