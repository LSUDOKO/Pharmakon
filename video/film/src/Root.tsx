import React from "react";
import { Composition, Folder } from "remotion";
import { Film, SceneSolo } from "./Film";
import { Thumbnail } from "./Thumbnail";
import { DevpostCard } from "./DevpostCard";
import { LogoSquare } from "./LogoSquare";
import { SCENES, TOTAL } from "./timing";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition id="Pharmakon" component={Film} durationInFrames={TOTAL} fps={30} width={1920} height={1080} />
      <Composition id="Thumbnail" component={Thumbnail} durationInFrames={1} fps={30} width={1920} height={1080} />
      <Composition id="DevpostCard" component={DevpostCard} durationInFrames={1} fps={30} width={1500} height={1000} />
      <Composition id="LogoSquare" component={LogoSquare} durationInFrames={1} fps={30} width={1000} height={1000} />
      <Folder name="Scenes">
        {SCENES.map((s) => (
          <Composition key={s.id} id={`scene-${s.id}`} component={SceneSolo} durationInFrames={s.duration} fps={30} width={1920} height={1080} defaultProps={{ id: s.id }} />
        ))}
      </Folder>
    </>
  );
};
