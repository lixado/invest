<script lang="ts">

</script>


<main>
    <div class="container">
        <div class="header">
            <div class="vertical-line">
                <div></div>
            </div>
            <br>
            <h1>Your Name</h1>
            <p>Title</p>
            <div class="contact-info">
                <p>123-456-7890</p>
                <p>hello@reallygreatsite.com</p>
                <p>www.reallygreatsite.com</p>
            </div>
        </div>

        <hr>

        <div class="section">
            <h2 class="section-title">ABOUT ME</h2>
            <p>Similar to a resume summary - about me is an introduction that provides a brief snapshot of your professional background, relevant skills, and key accomplishments.</p>
        </div>

        <hr>

        <div class="section two-columns" style="display: flex;">
            <div class="column education">
                <h2 class="section-title">EDUCATION</h2>
                <div>
                    <h3>Masters Degree in XX</h3>
                    <p>Jun 2010 - Mar 2012</p>
                    <p>School Here</p>
                    <p>Location</p>
                </div>
                <div>
                    <h3>Bachelors Degree in XX</h3>
                    <p>Jun 2002 - Mar 2006</p>
                    <p>School Here</p>
                    <p>Location</p>
                </div>
            </div>

            <div class="column work-experience">
                <h2 class="section-title">WORK EXPERIENCE</h2>
                <div>
                    <h3>COMPANY</h3>
                    <p>Indicate your role/position in the company</p>
                    <ul>
                        <li>Include relevant work experience on your resume to show hiring managers you've understood the requirements of the job.</li>
                        <li>Work experience section of your resume should contain specific information about your employment history.</li>
                        <li>Work experience section of your resume should contain specific information about your employment history.</li>
                    </ul>
                    <div class="date-location">
                        <span>Location</span>
                        <span>Date</span>
                    </div>
                </div>
                <div>
                    <h3>COMPANY</h3>
                    <p>Indicate your role/position in the company</p>
                    <ul>
                        <li>Include relevant work experience on your resume to show hiring managers you've understood the requirements of the job.</li>
                        <li>Work experience section of your resume should contain specific information about your employment history.</li>
                        <li>Work experience section of your resume should contain specific information about your employment history.</li>
                    </ul>
                    <div class="date-location">
                        <span>Location</span>
                        <span>Date</span>
                    </div>
                </div>
            </div>
        </div>

        <hr>

        <div class="section two-columns">
            <div class="column skills">
                <h2 class="section-title">SKILLS</h2>
                <ul>
                    <li>Time management</li>
                    <li>Communication</li>
                    <li>Critical thinking</li>
                    <li>Analytics</li>
                    <li>SEO</li>
                    <li>Communication</li>
                    <li>Project management</li>
                </ul>
            </div>

            <div class="column achievements">
                <h2 class="section-title">ACHIEVEMENTS</h2>
                <ul>
                    <li>Your achievement</li>
                    <li>Location</li>
                    <li>Date</li>
                </ul>
                <ul>
                    <li>Your achievement</li>
                    <li>Location</li>
                    <li>Date</li>
                </ul>
            </div>
        </div>
    </div>
</main>


<style>
    .container {
        max-width: 900px;
        margin: 0 auto;
        padding: 0px 20px 20px 20px;
        background-color: #fff;
        font-family: Arial, sans-serif;
        line-height: 1.6;
        background-color: #f4f4f4;
        color: #242424;
    }

    .vertical-line {
        display: flex;
        justify-content: center;
        align-items: flex-start;
    }

    .vertical-line div {
        width: 5px;
        height: 60px;
        background: #242424;
        z-index: 1;
        border-bottom-left-radius: 50px;
        border-bottom-right-radius: 50px;
    }

    .header, .section-title {
        text-align: center;
        margin-bottom: 20px;
    }

    .header h1 {
        margin: 0;
        font-size: 2.5em;
    }

    .header p {
        margin: 5px 0;
    }

    .contact-info {
        text-align: right;
        margin-top: -60px;
    }

    .contact-info p {
        margin: 5px 0;
    }

    .section {
        margin-bottom: 30px;
    }

    .two-columns {
        display: flex;
        justify-content: space-between;
    }

    .column {
        width: 48%;
    }

    .skills ul, .achievements ul {
        list-style-type: none;
        padding: 0;
    }

    .skills li, .achievements li {
        margin-bottom: 5px;
    }

    .work-experience ul {
        list-style-type: disc;
        margin: 0;
        padding-left: 20px;
    }

    .date-location {
        display: flex;
        justify-content: space-between;
        margin-top: 10px;
    }

    .date-location span {
        font-size: 0.9em;
        color: #242424;
    }

    hr {
        margin: 30px 0;
        border-top: 5px solid #242424;
        border-radius: 5px;
    }
</style>