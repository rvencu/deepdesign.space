from PIL import Image
import imagehash
import os
from collections import defaultdict


def dedup_image(directories):
    for label in directories:
        files = (file for file in os.listdir(label) if os.path.isfile(os.path.join(label, file)))
        d=defaultdict(list)
        for image in files:
            if image!=".DS_Store":
                im=Image.open('{}/{}'.format(label,image))
                h=str(imagehash.dhash(im))
                d[h]+=[image]
        lst=[]
        for k,v in d.items():
            if len(v)>1:
                lst.append(list(v))
        for item in lst:
            for image in item [1:]:
                print ('removing '+ image + ' from ' + label)
                os.unlink("{}/{}".format(label,image))

if __name__=="__main__":
    directories=['beach house interior design','minimalist interior design','Arts and Crafts interior design','Asian interior design','bauhaus interior design','Art Moderne interior design','Artisan interior design','Art Deco interior design','abstract interior design','nautical interior design','northwestern interior design','organic interior design','post-modern interior design','regence interior design','regency interior design','retro interior design','romantic interior design','scandinavian interior design','shabby chic interior design','shaker interior design','space age interior design','swedish interior design','traditional interior design','transitional interior design','coastal interior design','contemporary interior design','cottage interior design','country interior design','danish interior design','eclectic interior design','european interior design','finnish interior design','french interior design','greek interior design','industrial interior design','italian interior design','lake house interior design','medieval interior design','mediterranean interior design','memphis interior design','mid-century modern interior design','tropical interior design','urban interior design','venetian interior design','vintage interior design','western interior design','zen interior design','modern interior design','rustic interior design','rustic interior design', 'african interior design','American Colonial interior design','Amish interior design', 'arabian interior design','Art Nouveau interior design','Baroque interior design','Brazilian interior design', 'British Colonial interior design','Carolean interior design','Chinese interior design','Chippendale interior design','Commonwealth interior design','Directoire interior design','Dutch Renaissance interior design','Egyptian interior design','Empire interior design','English interior design','English Country interior design','Exploration interior design','Flemish interior design','French Provincial interior design','Georgian interior design','Gothic interior design','Indian interior design','Jacobean interior design','Japanese interior design','Machine Age interior design','Mexican interior design','Mission interior design','modernist interior design','Moroccan interior design','Neoclassic interior design','Old World interior design','Palladian interior design','Parisian interior design','Pennsylvania Dutch interior design','Plantation interior design','Queen Anne interior design','Regal interior design','Renaissance interior design','Revival interior design','Rietveld interior design','Rococo interior design','Russian interior design','Southwestern interior design','Spanish Renaissance interior design','Steampunk interior design','Tudor interior design','Tuscan interior design','Victorian interior design','William and Mary interior design']
    dedup_image(directories)
