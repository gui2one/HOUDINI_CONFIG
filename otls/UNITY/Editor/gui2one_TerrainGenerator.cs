using UnityEngine;
using System.Collections.Generic;
using UnityEditor;
using System.IO;
using UnityEngine.Windows;
using System;

public class gui2one_TerrainGenerator : EditorWindow
{

 
    [MenuItem("Terrain/Terrain Generator", false, 2000)]
    static void OpenWindow()
    {

        EditorWindow.GetWindow<gui2one_TerrainGenerator>(true);
    }



    //Prototypes
    //public Texture2D m_splat0, m_splat1;
    public float m_splatTileSize0 = 2.0f;
    public float m_splatTileSize1 = 2.0f;


    //Noise settings. A higher frq will create larger scale details. Each seed value will create a unique look
    public int m_groundSeed = 0;
    public float m_groundFrq = 800.0f;
    public int m_mountainSeed = 1;
    public float m_mountainFrq = 1200.0f;
    public int m_treeSeed = 2;
    public float m_treeFrq = 400.0f;
    public int m_detailSeed = 3;
    public float m_detailFrq = 100.0f;
    //Terrain settings
    public int m_tilesX = 1; //Number of terrain tiles on the x axis
    public int m_tilesZ = 1; //Number of terrain tiles on the z axis
    public float m_pixelMapError = 6.0f; //A lower pixel error will draw terrain at a higher Level of detail but will be slower
    public float m_baseMapDist = 1000.0f; //The distance at which the low res base map will be drawn. Decrease to increase performance
                                          //Terrain data settings
    public int m_heightMapSize = 513; //Higher number will create more detailed height maps
    public int m_alphaMapSize = 512; //This is the control map that controls how the splat textures will be blended
    
    public int m_terrainHeight = 300;
    public int m_detailMapSize = 2048; //Resolutions of detail (Grass) layers
                                       //Tree settings
    public int m_treeSpacing = 16; //spacing between trees
    public float m_treeDistance = 30.0f; //The distance at which trees will no longer be drawn
    public float m_treeBillboardDistance = 1.0f; //The distance at which trees meshes will turn into tree billboards
    public float m_treeCrossFadeLength = 20.0f; //As trees turn to billboards there transform is rotated to match the meshes, a higher number will make this transition smoother
    public int m_treeMaximumFullLODCount = 10; //The maximum number of trees that will be drawn in a certain area. 
                                               //Detail settings
    public DetailRenderMode detailMode;
    public int m_detailObjectDistance = 1000; //The distance at which details will no longer be drawn
    public float m_detailObjectDensity = 1.0f; //Creates more dense details within patch
    public int m_detailResolutionPerPatch = 64; //The size of detail patch. A higher number may reduce draw calls as details will be batch in larger patches
    public float m_wavingGrassStrength = 0.4f;
    public float m_wavingGrassAmount = 0.2f;
    public float m_wavingGrassSpeed = 0.4f;
    public Color m_wavingGrassTint = Color.white;
    public Color m_grassHealthyColor = Color.white;
    public Color m_grassDryColor = Color.white;

    //Private
    PerlinNoise m_groundNoise, m_mountainNoise, m_treeNoise, m_detailNoise;
    Terrain[,] m_terrain;
    SplatPrototype[] m_splatPrototypes;
    TreePrototype[] m_treeProtoTypes;
    DetailPrototype[] m_detailProtoTypes;
    Vector2 m_offset;


    public Texture2D m_splat0, m_splat1;
    public GameObject m_tree0, m_tree1, m_tree2;
    public Texture2D m_detail0, m_detail1, m_detail2;

    int resolution;
    FileStream heightMap;
    
    public string heightMapFile;
    string newPath = "";
    string oldPath = "";
    string ext = "";
    public int m_terrainSize = 1024;
    string m_splat0_path;
    string m_splat1_path;

    float waterLevel = 1.0f;


    float[,] m_heightValues;

    void OnFocus()
    {

        

    }

    void OnEnable()
    {
        loadData();
    }

    void OnGUI()
    {
        //GO = EditorGUILayout.ObjectField(GO, typeof(GameObject), true);

        //m_splat0 = (Texture2D)EditorGUILayout.ObjectField(m_splat0, typeof(Texture2D), true);


        float uiX = 0;
        float uiY = 0;
        float width = 64;



        EditorGUI.LabelField(new Rect(0, uiY, width, width), "m_splat0 :");
        EditorGUI.LabelField(new Rect(width + 10, uiY, width, width), "m_splat1 :");

        uiY += 20;
        m_splat0 = (Texture2D)EditorGUI.ObjectField(new Rect(0, uiY, width, width), m_splat0, typeof(Texture2D), true);

        m_splat1 = (Texture2D)EditorGUI.ObjectField(new Rect(width + 10, uiY, width, width), m_splat1, typeof(Texture2D), true);

        uiY += width + 20;
        EditorGUI.LabelField(new Rect(0, uiY, width, width), "Trees :");

        uiY += 20;
        m_tree0 = (GameObject)EditorGUI.ObjectField(new Rect(0, uiY, position.width - 6, 15), m_tree0, typeof(GameObject), true);
        uiY += 20;
        m_tree1 = (GameObject)EditorGUI.ObjectField(new Rect(0, uiY, position.width - 6, 15), m_tree1, typeof(GameObject), true);
        uiY += 20;
        m_tree2 = (GameObject)EditorGUI.ObjectField(new Rect(0, uiY, position.width - 6, 15), m_tree2, typeof(GameObject), true);

        uiY += 20;
        EditorGUI.LabelField(new Rect(0, uiY, width, width), "Grass :");

        uiY += 20;
        m_detail0 = (Texture2D)EditorGUI.ObjectField(new Rect(0, uiY, width, width), m_detail0, typeof(Texture2D), true);

        m_detail1 = (Texture2D)EditorGUI.ObjectField(new Rect(width + 10, uiY, width, width), m_detail1, typeof(Texture2D), true);

        m_detail2 = (Texture2D)EditorGUI.ObjectField(new Rect(width * 2 + 20, uiY, width, width), m_detail2, typeof(Texture2D), true);
        //m_splat1 = (Texture2D)EditorGUILayout.ObjectField(m_splat1, typeof(Texture2D), true);


        uiY += width + 20;

        EditorGUI.LabelField(new Rect(0, uiY, position.width, width), "Height Map :");
        uiY += 20;
        heightMapFile = EditorGUI.TextField(new Rect(0, uiY, position.width * 0.8f, 20.0f), newPath);

        if (GUI.Button(new Rect(position.width * 0.8f, uiY, position.width * 0.2f, 20.0f), "..."))
        {
            newPath = EditorUtility.OpenFilePanel("Load Houdini Asset", oldPath, ext);
            Debug.Log(newPath);
            byte[] data = File.ReadAllBytes(newPath);


            resolution = (int)Mathf.Sqrt(data.Length / 2);
        }


        uiY += width + 20;
        resolution = EditorGUI.IntField(new Rect(0, uiY, position.width, 20.0f), "Resolution", resolution);

        uiY += 20;
        EditorGUI.LabelField(new Rect(0, uiY, position.width, width), "Water Level :");
        uiY += 20;
        waterLevel = EditorGUI.Slider(new Rect(0, uiY, position.width, 20.0f), waterLevel, -50.0f, 3000.0f);

        uiY += 20;
        m_terrainSize = EditorGUI.IntField(new Rect(0, uiY, position.width, 20.0f), "Terrain Size", m_terrainSize);
        uiY += 20;
        m_terrainHeight = EditorGUI.IntField(new Rect(0, uiY, position.width, 20.0f), "Terrain Height", m_terrainHeight);
        //heightMap = System.IO.File.OpenRead(newPath);
        //Debug.Log(heightMap);
        //BinaryReader reader = new System.IO.BinaryReader(heightMap);
        //Debug.Log(reader);




        //addTerrain = EditorGUILayout.Vector3Field("Add terrain", addTerrain);
        //shiftHeight = EditorGUILayout.Slider("Shift height", shiftHeight, -1f, 1f);
        //bottomTopRadioSelected = GUILayout.SelectionGrid(bottomTopRadioSelected, bottomTopRadio, bottomTopRadio.Length, EditorStyles.radioButton);
        uiY += width + 20;
        if (GUI.Button(new Rect(0, uiY, position.width - 6, 20), "Create Terrain"))
        {
            Debug.Log(resolution + " ---<< RESOLUTION");
            m_heightValues = new float[resolution, resolution];

            GameObject existingTerrain = GameObject.Find("gui2one_terrain");
            if (existingTerrain != null)
            {
                Debug.Log("already have an object named gui2one_terrain");
                DestroyImmediate(existingTerrain);
                Debug.Log("destroyed ...");
            }

            Debug.Log("Creating new Terrain ...");
            Execute();

        }
    }

    void Execute()
    {


        m_groundNoise = new PerlinNoise(m_groundSeed);
        m_mountainNoise = new PerlinNoise(m_mountainSeed);
        m_treeNoise = new PerlinNoise(m_treeSeed);
        m_detailNoise = new PerlinNoise(m_detailSeed);

        if (!Mathf.IsPowerOfTwo(m_heightMapSize - 1))
        {
            Debug.Log("TerrianGenerator::Start - height map size must be pow2+1 number");
            m_heightMapSize = Mathf.ClosestPowerOfTwo(m_heightMapSize) + 1;
        }

        if (!Mathf.IsPowerOfTwo(m_alphaMapSize))
        {
            Debug.Log("TerrianGenerator::Start - Alpha map size must be pow2 number");
            m_alphaMapSize = Mathf.ClosestPowerOfTwo(m_alphaMapSize);
        }

        if (!Mathf.IsPowerOfTwo(m_detailMapSize))
        {
            Debug.Log("TerrianGenerator::Start - Detail map size must be pow2 number");
            m_detailMapSize = Mathf.ClosestPowerOfTwo(m_detailMapSize);
        }

        if (m_detailResolutionPerPatch < 8)
        {
            Debug.Log("TerrianGenerator::Start - Detail resolution per patch must be >= 8, changing to 8");
            m_detailResolutionPerPatch = 8;
        }

        float[,] htmap = new float[m_heightMapSize, m_heightMapSize];

        m_terrain = new Terrain[m_tilesX, m_tilesZ];

        //this will center terrain at origin
        m_offset = new Vector2(-m_terrainSize * m_tilesX * 0.5f, -m_terrainSize * m_tilesZ * 0.5f);

        CreateProtoTypes();

        for (int x = 0; x < m_tilesX; x++)
        {
            for (int z = 0; z < m_tilesZ; z++)
            {
                //FillHeights(htmap, x, z);

                TerrainData terrainData = new TerrainData();
                terrainData.heightmapResolution = resolution - 1;
                LoadHeightMap(heightMapFile, terrainData);
                

                terrainData.size = new Vector3(2048, 300, 2048);

                //terrainData.SetHeights(0, 0, htmap);
                terrainData.size = new Vector3(m_terrainSize, m_terrainHeight, m_terrainSize);
                terrainData.splatPrototypes = m_splatPrototypes;
                terrainData.treePrototypes = m_treeProtoTypes;
                terrainData.detailPrototypes = m_detailProtoTypes;

                LoadColorMap("Assets/Resources/height_maps/color_map_01.data", terrainData);
                //FillAlphaMap(terrainData);

                m_terrain[x, z] = Terrain.CreateTerrainGameObject(terrainData).GetComponent<Terrain>();
                m_terrain[x, z].transform.position = new Vector3(m_terrainSize * x + m_offset.x, 0, m_terrainSize * z + m_offset.y);
                m_terrain[x, z].heightmapPixelError = m_pixelMapError;
                m_terrain[x, z].basemapDistance = m_baseMapDist;

                //disable this for better frame rate
                m_terrain[x, z].castShadows = true;
                m_terrain[x, z].name = "gui2one_terrain";

                FillTreeInstances(m_terrain[x, z], x, z);
                FillDetailMap(m_terrain[x, z], x, z);
            }
        }

        //Set the neighbours of terrain to remove seams.
        for (int x = 0; x < m_tilesX; x++)
        {
            for (int z = 0; z < m_tilesZ; z++)
            {
                Terrain right = null;
                Terrain left = null;
                Terrain bottom = null;
                Terrain top = null;

                if (x > 0) left = m_terrain[(x - 1), z];
                if (x < m_tilesX - 1) right = m_terrain[(x + 1), z];

                if (z > 0) bottom = m_terrain[x, (z - 1)];
                if (z < m_tilesZ - 1) top = m_terrain[x, (z + 1)];

                m_terrain[x, z].SetNeighbors(left, top, right, bottom);

            }
        }

    }

    void LoadHeightMap(string aFileName, TerrainData aTerrain)
    {
        int h = aTerrain.heightmapHeight - 1;
        int w = aTerrain.heightmapWidth - 1;
        float[,] data = new float[h, w];
        using (var file = System.IO.File.OpenRead(aFileName))
        using (var reader = new System.IO.BinaryReader(file))
        {
            for (int y = 0; y < h; y++)
            {
                for (int x = 0; x < w; x++)
                {
                    float v = (float)reader.ReadUInt16() / 0xFFFF;
                    data[y, x] = v;
                }
            }
        }
        aTerrain.SetHeights(0, 0, data);
    }

    void LoadColorMap(string aFileName, TerrainData aTerrain)
    {

        using (var file = System.IO.File.OpenRead(aFileName))
        using (var reader = new System.IO.BinaryReader(file))
        {
            int h = aTerrain.heightmapHeight - 1;
            int w = aTerrain.heightmapWidth - 1;
            float[,] data = new float[h, w];
            float[,,] map = new float[m_alphaMapSize, m_alphaMapSize, 2];
            for (int x = 0; x < m_alphaMapSize; x++)
            {
                for (int z = 0; z < m_alphaMapSize; z++)
                {

                    float v = (float)reader.ReadUInt16() / 0xFFFF;

                    map[x, z, 0] = v;
                    map[x, z, 1] = 1.0f - v;

                }
            }
            aTerrain.alphamapResolution = m_alphaMapSize;
            aTerrain.SetAlphamaps(0, 0, map);
        }
       // aTerrain.SetAlphamaps(0, 0, map);





       




    }

    void CreateProtoTypes()
    {
        //Ive hard coded 2 splat prototypes, 3 tree prototypes and 3 detail prototypes.
        //This is a little inflexible way to do it but it made the code simpler and can easly be modified 

        m_splatPrototypes = new SplatPrototype[2];

        m_splatPrototypes[0] = new SplatPrototype();
        m_splatPrototypes[0].texture = (Texture2D)m_splat0;
        //m_splatPrototypes[0].normalMap = (Texture2D)m_splat0;
        m_splatPrototypes[0].tileSize = new Vector2(m_splatTileSize0, m_splatTileSize0);

        m_splatPrototypes[1] = new SplatPrototype();
        m_splatPrototypes[1].texture = (Texture2D)m_splat1;
        m_splatPrototypes[1].tileSize = new Vector2(m_splatTileSize1, m_splatTileSize1);

        m_treeProtoTypes = new TreePrototype[3];

        m_treeProtoTypes[0] = new TreePrototype();
        m_treeProtoTypes[0].prefab = m_tree0;


        m_treeProtoTypes[1] = new TreePrototype();
        m_treeProtoTypes[1].prefab = m_tree1;

        m_treeProtoTypes[2] = new TreePrototype();
        m_treeProtoTypes[2].prefab = m_tree2;

        m_detailProtoTypes = new DetailPrototype[3];

        m_detailProtoTypes[0] = new DetailPrototype();
        m_detailProtoTypes[0].prototypeTexture = m_detail0;
        m_detailProtoTypes[0].renderMode = DetailRenderMode.Grass;
        m_detailProtoTypes[0].healthyColor = m_grassHealthyColor;
        m_detailProtoTypes[0].dryColor = m_grassDryColor;

        m_detailProtoTypes[1] = new DetailPrototype();
        m_detailProtoTypes[1].prototypeTexture = m_detail1;
        m_detailProtoTypes[1].renderMode = DetailRenderMode.Grass;
        m_detailProtoTypes[1].healthyColor = m_grassHealthyColor;
        m_detailProtoTypes[1].dryColor = m_grassDryColor;
        //m_detailProtoTypes[1].minWidth = 0.5f;
        //m_detailProtoTypes[1].maxWidth = 1.0f;
        //m_detailProtoTypes[1].minHeight = 0.1f;
        //m_detailProtoTypes[1].maxHeight = 0.3f;

        m_detailProtoTypes[2] = new DetailPrototype();
        m_detailProtoTypes[2].prototypeTexture = m_detail2;
        m_detailProtoTypes[2].renderMode = DetailRenderMode.Grass;
        m_detailProtoTypes[2].healthyColor = m_grassHealthyColor;
        m_detailProtoTypes[2].dryColor = m_grassDryColor;
        //m_detailProtoTypes[2].minWidth = 0.5f;
        //m_detailProtoTypes[2].maxWidth = 1.0f;
        //m_detailProtoTypes[2].minHeight = 0.1f;
        //m_detailProtoTypes[2].maxHeight = 0.3f;

        //m_detailProtoTypes[3] = new DetailPrototype();
        //m_detailProtoTypes[3].usePrototypeMesh = true;
        //m_detailProtoTypes[3].prototype = (GameObject)Resources.Load("render_geo");
        //m_detailProtoTypes[3].renderMode = DetailRenderMode.VertexLit;
        //m_detailProtoTypes[3].healthyColor = Color.white;
        //m_detailProtoTypes[3].dryColor = Color.white;
        //m_detailProtoTypes[3].minWidth = 0.5f;
        //m_detailProtoTypes[3].maxWidth = 1.0f;
        //m_detailProtoTypes[3].minHeight = 0.1f;
        //m_detailProtoTypes[3].maxHeight = 0.3f;


    }

    void FillHeights(float[,] htmap, int tileX, int tileZ)
    {
        float ratio = (float)m_terrainSize / (float)m_heightMapSize;

        for (int x = 0; x < m_heightMapSize; x++)
        {
            for (int z = 0; z < m_heightMapSize; z++)
            {
                float worldPosX = (x + tileX * (m_heightMapSize - 1)) * ratio;
                float worldPosZ = (z + tileZ * (m_heightMapSize - 1)) * ratio;

                float mountains = Mathf.Max(0.0f, m_mountainNoise.FractalNoise2D(worldPosX, worldPosZ, 12, m_mountainFrq, 0.8f));

                float plain = m_groundNoise.FractalNoise2D(worldPosX, worldPosZ, 12, m_groundFrq, 0.1f) + 0.1f;

                htmap[z, x] = plain + mountains;
            }
        }
    }

    void FillAlphaMap(TerrainData terrainData)
    {
        float[,,] map = new float[m_alphaMapSize, m_alphaMapSize, 2];

        UnityEngine.Random.seed = 0;

        for (int x = 0; x < m_alphaMapSize; x++)
        {
            for (int z = 0; z < m_alphaMapSize; z++)
            {
                // Get the normalized terrain coordinate that
                // corresponds to the the point.
                float normX = x * 1.0f / (m_alphaMapSize - 1);
                float normZ = z * 1.0f / (m_alphaMapSize - 1);

                // Get the steepness value at the normalized coordinate.
                float angle = terrainData.GetSteepness(normX, normZ);

                // Steepness is given as an angle, 0..90 degrees. Divide
                // by 90 to get an alpha blending value in the range 0..1.
                float frac = angle / 90.0f;
                map[z, x, 0] = frac;
                map[z, x, 1] = 1.0f - frac;

            }
        }

        terrainData.alphamapResolution = m_alphaMapSize;
        terrainData.SetAlphamaps(0, 0, map);
    }
    
    void FillTreeInstances(Terrain terrain, int tileX, int tileZ)
    {
        UnityEngine.Random.seed = 0;

        for (int x = 0; x < m_terrainSize; x += m_treeSpacing)
        {
            for (int z = 0; z < m_terrainSize; z += m_treeSpacing)
            {

                float unit = 1.0f / (m_terrainSize - 1);

                float offsetX = UnityEngine.Random.value * unit * m_treeSpacing;
                float offsetZ = UnityEngine.Random.value * unit * m_treeSpacing;

                float normX = x * unit + offsetX;
                float normZ = z * unit + offsetZ;

                // Get the steepness value at the normalized coordinate.
                float angle = terrain.terrainData.GetSteepness(normX, normZ);

                // Steepness is given as an angle, 0..90 degrees. Divide
                // by 90 to get an alpha blending value in the range 0..1.
                float frac = angle / 90.0f;

                if (frac < 0.3f) //make sure tree are not on steep slopes
                {
                    float worldPosX = x + tileX * (m_terrainSize - 1);
                    float worldPosZ = z + tileZ * (m_terrainSize - 1);

                    float noise = m_treeNoise.FractalNoise2D(worldPosX, worldPosZ, 3, m_treeFrq, 1.0f);
                    //float noise = 1.0f;
                    float ht = terrain.terrainData.GetInterpolatedHeight(normX, normZ);

                    if (noise > 0.2f && ht < m_terrainHeight * 0.9f && ht > waterLevel)
                    {

                        TreeInstance temp = new TreeInstance();
                        temp.position = new Vector3(normX, ht, normZ);
                        temp.prototypeIndex = UnityEngine.Random.Range(0, 3);
                        temp.widthScale = 1;
                        temp.heightScale = 1;
                        temp.color = Color.white;
                        temp.lightmapColor = Color.white;

                        terrain.AddTreeInstance(temp);
                    }
                }

            }
        }

        terrain.treeDistance = m_treeDistance;

        terrain.treeBillboardDistance = m_treeBillboardDistance;
        terrain.treeCrossFadeLength = m_treeCrossFadeLength;
        terrain.treeMaximumFullLODCount = m_treeMaximumFullLODCount;

    }

    void FillDetailMap(Terrain terrain, int tileX, int tileZ)
    {
        //each layer is drawn separately so if you have a lot of layers your draw calls will increase 
        int[,] detailMap0 = new int[m_detailMapSize, m_detailMapSize];
        int[,] detailMap1 = new int[m_detailMapSize, m_detailMapSize];
        int[,] detailMap2 = new int[m_detailMapSize, m_detailMapSize];
        int[,] detailMap3 = new int[m_detailMapSize, m_detailMapSize];

        float ratio = (float)m_terrainSize / (float)m_detailMapSize;

        UnityEngine.Random.seed = 0;

        for (int x = 0; x < m_detailMapSize; x++)
        {
            for (int z = 0; z < m_detailMapSize; z++)
            {
                detailMap0[z, x] = 0;
                detailMap1[z, x] = 0;
                detailMap2[z, x] = 0;

                float unit = 1.0f / (m_detailMapSize - 1);

                float normX = x * unit;
                float normZ = z * unit;

                // Get the steepness value at the normalized coordinate.
                float angle = terrain.terrainData.GetSteepness(normX, normZ);

                // Steepness is given as an angle, 0..90 degrees. Divide
                // by 90 to get an alpha blending value in the range 0..1.
                float frac = angle / 90.0f;

                if (frac < 0.5f)
                {
                    float worldPosX = (x + tileX * (m_detailMapSize - 1)) * ratio;
                    float worldPosZ = (z + tileZ * (m_detailMapSize - 1)) * ratio;

                    //float noise = m_detailNoise.FractalNoise2D(worldPosX, worldPosZ, 3, m_detailFrq, 1.0f);
                    float noise = 1.0f;

                    if (noise > 0.0f)
                    {
                        float rnd = UnityEngine.Random.value;
                        //Randomly select what layer to use
                        if (rnd < 0.33f)
                            detailMap0[z, x] = 5;
                        else if (rnd < 0.66f)
                            detailMap1[z, x] = 5;
                        else if (rnd > 0.99)
                            detailMap3[z, x] = 1;
                        else
                            detailMap2[z, x] = 5;
                    }
                }

            }
        }

        terrain.terrainData.wavingGrassStrength = m_wavingGrassStrength;
        terrain.terrainData.wavingGrassAmount = m_wavingGrassAmount;
        terrain.terrainData.wavingGrassSpeed = m_wavingGrassSpeed;
        terrain.terrainData.wavingGrassTint = m_wavingGrassTint;
        terrain.detailObjectDensity = m_detailObjectDensity;
        terrain.detailObjectDistance = m_detailObjectDistance;
        terrain.terrainData.SetDetailResolution(m_detailMapSize, m_detailResolutionPerPatch);

        terrain.terrainData.SetDetailLayer(0, 0, 0, detailMap0);
        terrain.terrainData.SetDetailLayer(0, 0, 1, detailMap1);
        terrain.terrainData.SetDetailLayer(0, 0, 2, detailMap2);
       // terrain.terrainData.SetDetailLayer(0, 0, 3, detailMap3);


        terrain.Flush();
    }


    void OnDestroy()
    {
        saveData();
        Debug.Log("save DATA !!!!!!!!!!!!!!!");
    }
    void saveData()
    {

        StreamWriter sw = new StreamWriter("test.txt");
        sw.WriteLine("m_splat0="+AssetDatabase.GetAssetPath(m_splat0));
        sw.WriteLine("m_splat1=" + AssetDatabase.GetAssetPath(m_splat1));

        sw.WriteLine("m_detail0=" + AssetDatabase.GetAssetPath(m_detail0));
        sw.WriteLine("m_detail1=" + AssetDatabase.GetAssetPath(m_detail1));
        sw.WriteLine("m_detail2=" + AssetDatabase.GetAssetPath(m_detail2));

        sw.WriteLine("m_tree0=" + AssetDatabase.GetAssetPath(m_tree0));
        sw.WriteLine("m_tree1="+AssetDatabase.GetAssetPath(m_tree1));
        sw.WriteLine("m_tree2="+AssetDatabase.GetAssetPath(m_tree2));

        sw.WriteLine("heightMapFile="+heightMapFile);
        sw.WriteLine("resolution="+resolution);

        sw.WriteLine("waterLevel=" + waterLevel);
        sw.WriteLine("m_terrainSize=" + m_terrainSize);
        sw.WriteLine("m_terrainHeight=" + m_terrainHeight);

        sw.Close();
    }

    void loadData()
    {

        string line;
        StreamReader sr = new StreamReader("test.txt");
        while ((line = sr.ReadLine()) != null) {
            string[] s = line.Split("="[0]);
            Debug.Log(s[0] +" ---> "+ s[1]);
            if (s[0] == "m_splat0")
            {
                m_splat0 = (Texture2D)AssetDatabase.LoadAssetAtPath<Texture2D>(s[1]);
                Debug.Log("heyyyyyyyyyyyyyyyyyy");
            }
                
            else if (s[0] == "m_splat1" && s[1]  != "")
                m_splat1 = (Texture2D)AssetDatabase.LoadAssetAtPath<Texture2D>(s[1]);

            else if (s[0] == "m_detail0" && s[1] != "")
                m_detail0 = (Texture2D)AssetDatabase.LoadAssetAtPath<Texture2D>(s[1]);
            else if (s[0] == "m_detail1" && s[1] != "")
                m_detail1 = (Texture2D)AssetDatabase.LoadAssetAtPath<Texture2D>(s[1]);
            else if (s[0] == "m_detail2" && s[1] != "")
                m_detail2 = (Texture2D)AssetDatabase.LoadAssetAtPath<Texture2D>(s[1]);

            else if (s[0] == "m_tree0" && s[1] != "")
                m_tree0 = AssetDatabase.LoadAssetAtPath<GameObject>(s[1]);

            else if (s[0] == "m_tree1" && s[1] != "")
                m_tree1 = AssetDatabase.LoadAssetAtPath<GameObject>(s[1]);

            else if (s[0] == "m_tree2" && s[1] != "")
                m_tree2 = AssetDatabase.LoadAssetAtPath<GameObject>(s[1]);

            else if (s[0] == "heightMapFile" && s[1] != "")
                newPath = s[1];

            else if (s[0] == "resolution" && s[1] != "")
                resolution = Int32.Parse(s[1]);

            else if (s[0] == "waterLevel" && s[1] != "")
                waterLevel = float.Parse(s[1]);

            else if (s[0] == "m_terrainSize" && s[1] != "")
                m_terrainSize = Int32.Parse(s[1]);
            else if (s[0] == "m_terrainHeight" && s[1] != "")
                m_terrainHeight = Int32.Parse(s[1]);

        }
        sr.Close();
        

    }
}


